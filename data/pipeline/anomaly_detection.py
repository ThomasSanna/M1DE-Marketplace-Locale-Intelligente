"""
anomaly_detection.py — Détection d'anomalies transactionnelles (Isolation Forest).
Sprint 3 — Daniel (Data Engineer)

Algorithme :
  1. Extraction des features via etl_anomalies
  2. Normalisation (StandardScaler)
  3. Isolation Forest avec contamination automatique
  4. Labeling des types d'anomalies
  5. Stockage dans anomalies + anomaly_runs
"""

import json
import logging
from datetime import datetime, timezone

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from .db import get_connection, get_engine
from .etl_anomalies import extract_anomaly_features

logger = logging.getLogger(__name__)

NUMERIC_FEATURES = [
    "order_amount", "n_items", "avg_item_price",
    "hour_of_day", "day_of_week", "days_since_last_order",
    "client_avg_basket", "amount_vs_avg_ratio",
]

# Contamination cible : proportion attendue d'anomalies (~5% erreurs simulées + outliers)
DEFAULT_CONTAMINATION = 0.08


def label_anomaly_type(row) -> str:
    """Attribue un type d'anomalie basé sur les features de la transaction.

    Types possibles :
      - "Paiement echoue"           : paiement en échec (non simulé)
      - "Erreur simulee"            : erreur volontaire du simulateur (5%)
      - "Montant anormalement eleve": ratio montant/panier moyen > 3
      - "Montant anormalement bas"  : ratio montant/panier moyen < 0.1
      - "Frequence inhabituelle"    : temps entre commandes < 1 jour
      - "Horaire atypique"          : commande entre 1h et 5h du matin
      - "Panier suspect"            : nombre d'articles très élevé
      - "Anomalie non classifiee"   : aucun pattern connu détecté
    """
    if row["payment_failed"] and not row["is_simulated_error"]:
        return "Paiement echoue"
    if row["payment_failed"] and row["is_simulated_error"]:
        return "Erreur simulee"
    if row["amount_vs_avg_ratio"] > 3.0:
        return "Montant anormalement eleve"
    if row["amount_vs_avg_ratio"] < 0.1 and row["order_amount"] > 0:
        return "Montant anormalement bas"
    if 0 < row["days_since_last_order"] < 1:
        return "Frequence inhabituelle"
    if 1 <= row["hour_of_day"] <= 5:
        return "Horaire atypique"
    if row["n_items"] > 20:
        return "Panier suspect"
    return "Anomalie non classifiee"


def run_anomaly_detection(conn=None, engine=None,
                          contamination: float = DEFAULT_CONTAMINATION) -> int:
    """Exécute le pipeline complet de détection d'anomalies.

    Returns:
        run_id de l'exécution dans anomaly_runs
    """
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    if engine is None:
        engine = get_engine()

    cur = conn.cursor()

    try:
        # 1. ETL
        df = extract_anomaly_features(engine)
        if df.empty:
            logger.warning("Aucune transaction trouvée — détection annulée.")
            return -1

        # 2. Normalisation
        X = df[NUMERIC_FEATURES].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 3. Isolation Forest
        logger.info(f"Isolation Forest (contamination={contamination})...")
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=200,
            n_jobs=-1,
        )
        predictions = iso_forest.fit_predict(X_scaled)
        scores = iso_forest.decision_function(X_scaled)

        # -1 = anomalie, 1 = normal dans sklearn
        df["is_anomaly"] = predictions == -1
        # Inverser le score pour que plus élevé = plus anormal
        df["anomaly_score"] = -scores

        anomalies_df = df[df["is_anomaly"]].copy()
        n_anomalies = len(anomalies_df)

        logger.info(f"  {n_anomalies} anomalies détectées sur {len(df)} transactions "
                     f"({n_anomalies / len(df) * 100:.1f}%)")

        # 4. Labeling
        anomalies_df["anomaly_type"] = anomalies_df.apply(label_anomaly_type, axis=1)

        logger.info("Distribution des types d'anomalies :")
        for atype, count in anomalies_df["anomaly_type"].value_counts().items():
            logger.info(f"  {atype}: {count}")

        # 5. Stockage en base
        params = {
            "algorithm": "IsolationForest",
            "contamination": contamination,
            "n_estimators": 200,
            "random_state": 42,
            "features": NUMERIC_FEATURES,
            "scaler": "StandardScaler",
            "total_transactions": len(df),
        }

        cur.execute(
            """
            INSERT INTO anomaly_runs (algorithm, contamination, parameters, status)
            VALUES ('IsolationForest', %s, %s, 'running')
            RETURNING id
            """,
            (contamination, json.dumps(params)),
        )
        run_id = cur.fetchone()[0]

        rows = []
        for _, row in anomalies_df.iterrows():
            rows.append((
                run_id,
                str(row["order_id"]),
                str(row["client_id"]),
                float(round(row["anomaly_score"], 4)),
                row["anomaly_type"],
                float(row["order_amount"]),
                bool(row["payment_failed"]),
                bool(row["is_simulated_error"]),
                int(row["n_items"]),
                float(row["avg_item_price"]),
                int(row["hour_of_day"]),
                int(row["day_of_week"]),
                int(row["days_since_last_order"]),
                float(row["client_avg_basket"]),
                float(round(row["amount_vs_avg_ratio"], 4)),
            ))

        cur.executemany(
            """
            INSERT INTO anomalies
                (run_id, order_id, client_id, anomaly_score, anomaly_type,
                 order_amount, payment_failed, is_simulated_error,
                 n_items, avg_item_price, hour_of_day, day_of_week,
                 days_since_last_order, client_avg_basket, amount_vs_avg_ratio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )

        # Marquer le run comme terminé
        cur.execute(
            """
            UPDATE anomaly_runs
            SET finished_at = %s, n_anomalies = %s, status = 'success'
            WHERE id = %s
            """,
            (datetime.now(timezone.utc), n_anomalies, run_id),
        )

        conn.commit()
        logger.info(f"Détection d'anomalies terminée : run_id={run_id}, "
                     f"{n_anomalies} anomalies détectées")
        return run_id

    except Exception:
        conn.rollback()
        try:
            cur.execute(
                "UPDATE anomaly_runs SET status = 'failed', finished_at = NOW() "
                "WHERE status = 'running'"
            )
            conn.commit()
        except Exception:
            pass
        raise
    finally:
        cur.close()
        if own_conn:
            conn.close()
