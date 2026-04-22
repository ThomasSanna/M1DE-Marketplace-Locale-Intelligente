"""
clustering_customers.py — Segmentation K-Means des clients.
Sprint 2 — Daniel (Data Engineer)

Algorithme :
  1. Extraction des features via etl_customers
  2. Normalisation (StandardScaler)
  3. Recherche du K optimal (silhouette score, K=2..8)
  4. K-Means final avec labeling automatique des clusters
  5. Stockage dans customer_segments + clustering_runs
"""

import json
import logging
from datetime import datetime, timezone

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .db import get_connection, get_engine
from .etl_customers import extract_customer_features

logger = logging.getLogger(__name__)

NUMERIC_FEATURES = [
    "recency_days", "frequency", "monetary",
    "avg_basket", "cancellation_rate", "days_since_registration",
]


def find_optimal_k(X_scaled: np.ndarray, k_range=range(2, 9)) -> tuple[int, dict]:
    """Évalue K-Means pour chaque K et retourne le meilleur K (silhouette).

    Returns:
        (best_k, metrics_dict) où metrics_dict[k] = {silhouette, inertia}
    """
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


def label_customer_clusters(centroids: np.ndarray, feature_names: list[str]) -> dict[int, str]:
    """Attribue un label humain à chaque cluster en analysant les centroïdes.

    Stratégie basée sur les valeurs relatives des features RFM :
      - recency élevée + frequency faible    → "Clients dormants"
      - frequency élevée + monetary élevé    → "Fideles premium"
      - frequency élevée + monetary faible   → "Acheteurs impulsifs"
      - monetary élevé + frequency faible    → "Gros paniers occasionnels"
    """
    n_clusters = centroids.shape[0]
    labels = {}

    # Indices des features
    idx = {name: i for i, name in enumerate(feature_names)}

    # Calculer les médianes de chaque feature pour le seuil haut/bas
    medians = np.median(centroids, axis=0)

    for cluster_id in range(n_clusters):
        c = centroids[cluster_id]

        high_recency = c[idx["recency_days"]] > medians[idx["recency_days"]]
        high_freq = c[idx["frequency"]] > medians[idx["frequency"]]
        high_monetary = c[idx["monetary"]] > medians[idx["monetary"]]
        high_cancel = c[idx["cancellation_rate"]] > medians[idx["cancellation_rate"]]

        if high_recency and not high_freq:
            labels[cluster_id] = "Clients dormants"
        elif high_freq and high_monetary and not high_cancel:
            labels[cluster_id] = "Fideles premium"
        elif high_freq and not high_monetary:
            labels[cluster_id] = "Acheteurs impulsifs"
        elif high_monetary and not high_freq:
            labels[cluster_id] = "Gros paniers occasionnels"
        elif high_cancel:
            labels[cluster_id] = "Clients a risque"
        elif not high_freq and not high_monetary:
            labels[cluster_id] = "Acheteurs occasionnels"
        else:
            labels[cluster_id] = f"Segment client {cluster_id + 1}"

    # Dédoublonner les labels en ajoutant un suffixe si nécessaire
    seen = {}
    for cluster_id, label in labels.items():
        if label in seen:
            seen[label] += 1
            labels[cluster_id] = f"{label} ({seen[label]})"
        else:
            seen[label] = 1

    return labels


def run_customer_clustering(conn=None, engine=None) -> int:
    """Exécute le pipeline complet de clustering clients.

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
        df = extract_customer_features(engine)
        if df.empty:
            logger.warning("Aucun client trouvé — clustering annulé.")
            return -1

        # 2. Normalisation
        X = df[NUMERIC_FEATURES].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 3. Recherche du K optimal
        logger.info("Recherche du K optimal (clients)...")
        best_k, metrics = find_optimal_k(X_scaled)

        # 4. Clustering final
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df["cluster_id"] = kmeans.fit_predict(X_scaled)

        sil_score = silhouette_score(X_scaled, df["cluster_id"])
        inertia = kmeans.inertia_

        # 5. Labeling
        centroids_original = scaler.inverse_transform(kmeans.cluster_centers_)
        cluster_labels = label_customer_clusters(centroids_original, NUMERIC_FEATURES)
        df["cluster_label"] = df["cluster_id"].map(cluster_labels)

        logger.info("Distribution des clusters clients :")
        for label, count in df["cluster_label"].value_counts().items():
            logger.info(f"  {label}: {count} clients")

        # 6. Stockage en base
        params = {
            "scaler": "StandardScaler",
            "random_state": 42,
            "n_init": 10,
            "k_range": "2-8",
            "metrics": {str(k): v for k, v in metrics.items()},
        }

        cur.execute(
            """
            INSERT INTO clustering_runs (run_type, n_clusters, parameters, status)
            VALUES ('customer', %s, %s, 'running')
            RETURNING id
            """,
            (best_k, json.dumps(params)),
        )
        run_id = cur.fetchone()[0]

        # Insertion des segments
        rows = []
        for _, row in df.iterrows():
            rows.append((
                run_id,
                str(row["user_id"]),
                int(row["cluster_id"]),
                row["cluster_label"],
                int(row["recency_days"]),
                int(row["frequency"]),
                float(row["monetary"]),
                float(row["avg_basket"]),
                row["favorite_category"],
                float(row["cancellation_rate"]),
                int(row["days_since_registration"]),
            ))

        cur.executemany(
            """
            INSERT INTO customer_segments
                (run_id, user_id, cluster_id, cluster_label,
                 recency_days, frequency, monetary, avg_basket,
                 favorite_category, cancellation_rate, days_since_registration)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )

        # Marquer le run comme terminé
        cur.execute(
            """
            UPDATE clustering_runs
            SET finished_at = %s, silhouette_score = %s, inertia = %s, status = 'success'
            WHERE id = %s
            """,
            (datetime.now(timezone.utc), float(round(sil_score, 4)), float(round(inertia, 2)), run_id),
        )

        conn.commit()
        logger.info(f"Clustering clients terminé : run_id={run_id}, K={best_k}, "
                     f"silhouette={sil_score:.4f}")
        return run_id

    except Exception:
        conn.rollback()
        # Tenter de marquer le run comme échoué
        try:
            cur.execute(
                "UPDATE clustering_runs SET status = 'failed', finished_at = NOW() "
                "WHERE status = 'running' AND run_type = 'customer'"
            )
            conn.commit()
        except Exception:
            pass
        raise
    finally:
        cur.close()
        if own_conn:
            conn.close()
