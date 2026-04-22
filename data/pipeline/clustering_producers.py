"""
clustering_producers.py — Segmentation K-Means des producteurs.
Sprint 2 — Daniel (Data Engineer)

Algorithme :
  1. Extraction des features via etl_producers
  2. Normalisation (StandardScaler)
  3. Recherche du K optimal (silhouette score, K=2..6)
  4. K-Means final avec labeling automatique des clusters
  5. Stockage dans producer_segments + clustering_runs
"""

import json
import logging
from datetime import datetime, timezone

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .db import get_connection, get_engine
from .etl_producers import extract_producer_features

logger = logging.getLogger(__name__)

NUMERIC_FEATURES = [
    "n_products", "n_categories", "total_revenue",
    "n_orders_received", "avg_order_value", "days_active",
]


def find_optimal_k(X_scaled: np.ndarray, k_range=range(2, 7)) -> tuple[int, dict]:
    """Évalue K-Means pour chaque K et retourne le meilleur K (silhouette)."""
    metrics = {}
    best_k, best_score = 2, -1

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels)
        metrics[k] = {"silhouette": round(sil, 4), "inertia": round(km.inertia_, 2)}
        logger.info(f"  K={k}: silhouette={sil:.4f}, inertia={km.inertia_:.2f}")

        if sil > best_score:
            best_score = sil
            best_k = k

    logger.info(f"  -> K optimal = {best_k} (silhouette={best_score:.4f})")
    return best_k, metrics


def label_producer_clusters(centroids: np.ndarray, feature_names: list[str]) -> dict[int, str]:
    """Attribue un label humain à chaque cluster de producteurs.

    Stratégie :
      - revenue élevé + diversité élevée → "Gros producteur diversifie"
      - revenue modéré + faible diversité → "Artisan de niche"
      - faible ancienneté + peu de commandes → "Nouveau producteur"
      - faible revenue + ancienneté élevée → "Producteur en declin"
    """
    n_clusters = centroids.shape[0]
    labels = {}

    idx = {name: i for i, name in enumerate(feature_names)}
    medians = np.median(centroids, axis=0)

    for cluster_id in range(n_clusters):
        c = centroids[cluster_id]

        high_revenue = c[idx["total_revenue"]] > medians[idx["total_revenue"]]
        high_diversity = c[idx["n_categories"]] > medians[idx["n_categories"]]
        high_activity = c[idx["days_active"]] > medians[idx["days_active"]]
        high_orders = c[idx["n_orders_received"]] > medians[idx["n_orders_received"]]

        if high_revenue and high_diversity:
            labels[cluster_id] = "Gros producteur diversifie"
        elif not high_diversity and high_orders:
            labels[cluster_id] = "Artisan de niche"
        elif not high_activity and not high_orders:
            labels[cluster_id] = "Nouveau producteur"
        elif not high_revenue and high_activity:
            labels[cluster_id] = "Producteur en declin"
        else:
            labels[cluster_id] = f"Segment producteur {cluster_id + 1}"

    # Dédoublonner
    seen = {}
    for cluster_id, label in labels.items():
        if label in seen:
            seen[label] += 1
            labels[cluster_id] = f"{label} ({seen[label]})"
        else:
            seen[label] = 1

    return labels


def run_producer_clustering(conn=None, engine=None) -> int:
    """Exécute le pipeline complet de clustering producteurs.

    Returns:
        run_id de l'exécution dans clustering_runs
    """
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    if engine is None:
        engine = get_engine()

    cur = conn.cursor()

    try:
        # 1. ETL
        df = extract_producer_features(engine)
        if df.empty:
            logger.warning("Aucun producteur trouvé — clustering annulé.")
            return -1

        # 2. Normalisation
        X = df[NUMERIC_FEATURES].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 3. Recherche du K optimal
        logger.info("Recherche du K optimal (producteurs)...")
        best_k, metrics = find_optimal_k(X_scaled)

        # 4. Clustering final
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df["cluster_id"] = kmeans.fit_predict(X_scaled)

        sil_score = silhouette_score(X_scaled, df["cluster_id"])
        inertia = kmeans.inertia_

        # 5. Labeling
        centroids_original = scaler.inverse_transform(kmeans.cluster_centers_)
        cluster_labels = label_producer_clusters(centroids_original, NUMERIC_FEATURES)
        df["cluster_label"] = df["cluster_id"].map(cluster_labels)

        logger.info("Distribution des clusters producteurs :")
        for label, count in df["cluster_label"].value_counts().items():
            logger.info(f"  {label}: {count} producteurs")

        # 6. Stockage en base
        params = {
            "scaler": "StandardScaler",
            "random_state": 42,
            "n_init": 10,
            "k_range": "2-6",
            "metrics": {str(k): v for k, v in metrics.items()},
        }

        cur.execute(
            """
            INSERT INTO clustering_runs (run_type, n_clusters, parameters, status)
            VALUES ('producer', %s, %s, 'running')
            RETURNING id
            """,
            (best_k, json.dumps(params)),
        )
        run_id = cur.fetchone()[0]

        rows = []
        for _, row in df.iterrows():
            rows.append((
                run_id,
                str(row["producer_id"]),
                int(row["cluster_id"]),
                row["cluster_label"],
                int(row["n_products"]),
                int(row["n_categories"]),
                float(row["total_revenue"]),
                float(row["avg_order_value"]),
                int(row["n_orders_received"]),
                int(row["days_active"]),
                row["location_region"],
            ))

        cur.executemany(
            """
            INSERT INTO producer_segments
                (run_id, producer_id, cluster_id, cluster_label,
                 n_products, n_categories, total_revenue, avg_order_value,
                 n_orders_received, days_active, location_region)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )

        cur.execute(
            """
            UPDATE clustering_runs
            SET finished_at = %s, silhouette_score = %s, inertia = %s, status = 'success'
            WHERE id = %s
            """,
            (datetime.now(timezone.utc), float(round(sil_score, 4)), float(round(inertia, 2)), run_id),
        )

        conn.commit()
        logger.info(f"Clustering producteurs terminé : run_id={run_id}, K={best_k}, "
                     f"silhouette={sil_score:.4f}")
        return run_id

    except Exception:
        conn.rollback()
        try:
            cur.execute(
                "UPDATE clustering_runs SET status = 'failed', finished_at = NOW() "
                "WHERE status = 'running' AND run_type = 'producer'"
            )
            conn.commit()
        except Exception:
            pass
        raise
    finally:
        cur.close()
        if own_conn:
            conn.close()
