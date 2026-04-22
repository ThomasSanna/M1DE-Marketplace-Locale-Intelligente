"""
etl_anomalies.py — Extraction des features transactionnelles pour la détection d'anomalies.
Sprint 3 — Daniel (Data Engineer)

Features extraites par transaction :
  - order_amount         : montant total de la commande
  - payment_failed       : le paiement a-t-il échoué ?
  - is_simulated_error   : l'erreur est-elle simulée (flag 5%) ?
  - n_items              : nombre d'articles dans la commande
  - avg_item_price       : prix moyen par article
  - hour_of_day          : heure de la commande (0-23)
  - day_of_week          : jour de la semaine (0=lundi, 6=dimanche)
  - days_since_last_order: jours depuis la commande précédente du client
  - client_avg_basket    : panier moyen historique du client
  - amount_vs_avg_ratio  : ratio montant commande / panier moyen client
"""

import logging

import pandas as pd

from .db import get_engine, query_df

logger = logging.getLogger(__name__)

ANOMALY_FEATURES_SQL = """
WITH order_details AS (
    SELECT
        o.id                                        AS order_id,
        o.client_id,
        o.total_amount                              AS order_amount,
        o.status                                    AS order_status,
        o.created_at                                AS order_date,
        EXTRACT(HOUR FROM o.created_at)             AS hour_of_day,
        EXTRACT(ISODOW FROM o.created_at) - 1       AS day_of_week,
        COUNT(oi.id)                                AS n_items,
        COALESCE(AVG(oi.unit_price_snapshot), 0)    AS avg_item_price
    FROM orders o
    LEFT JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.client_id, o.total_amount, o.status, o.created_at
),
payment_info AS (
    SELECT
        p.order_id,
        (p.status = 'failed')                      AS payment_failed,
        p.is_simulated_error
    FROM payments p
),
client_stats AS (
    SELECT
        o.client_id,
        AVG(o.total_amount)                         AS client_avg_basket
    FROM orders o
    WHERE o.status NOT IN ('draft', 'cancelled')
    GROUP BY o.client_id
),
prev_orders AS (
    SELECT
        o.id                                        AS order_id,
        COALESCE(
            EXTRACT(DAY FROM o.created_at - LAG(o.created_at) OVER (
                PARTITION BY o.client_id ORDER BY o.created_at
            )),
            -1
        )                                           AS days_since_last_order
    FROM orders o
)
SELECT
    od.order_id,
    od.client_id,
    od.order_amount,
    od.order_status,
    od.order_date,
    COALESCE(pi.payment_failed, FALSE)              AS payment_failed,
    COALESCE(pi.is_simulated_error, FALSE)          AS is_simulated_error,
    od.n_items,
    od.avg_item_price,
    od.hour_of_day::INTEGER,
    od.day_of_week::INTEGER,
    COALESCE(po.days_since_last_order, -1)::INTEGER AS days_since_last_order,
    COALESCE(cs.client_avg_basket, 0)               AS client_avg_basket,
    CASE
        WHEN COALESCE(cs.client_avg_basket, 0) > 0
        THEN od.order_amount / cs.client_avg_basket
        ELSE 1.0
    END                                             AS amount_vs_avg_ratio
FROM order_details od
LEFT JOIN payment_info  pi ON pi.order_id = od.order_id
LEFT JOIN client_stats  cs ON cs.client_id = od.client_id
LEFT JOIN prev_orders   po ON po.order_id = od.order_id
WHERE od.order_status != 'draft'
"""


def extract_anomaly_features(engine=None) -> pd.DataFrame:
    """Extrait les features transactionnelles pour la détection d'anomalies.

    Returns:
        DataFrame avec une ligne par transaction (commande non-draft).
    """
    if engine is None:
        engine = get_engine()

    logger.info("Extraction des features d'anomalies...")
    df = query_df(ANOMALY_FEATURES_SQL, engine)

    # Nettoyage
    numeric_cols = [
        "order_amount", "n_items", "avg_item_price",
        "hour_of_day", "day_of_week", "days_since_last_order",
        "client_avg_basket", "amount_vs_avg_ratio",
    ]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Remplacer days_since_last_order = -1 (première commande) par la médiane
    median_days = df.loc[df["days_since_last_order"] > 0, "days_since_last_order"].median()
    if pd.notna(median_days):
        df.loc[df["days_since_last_order"] < 0, "days_since_last_order"] = median_days

    logger.info(f"  {len(df)} transactions extraites")
    for col in numeric_cols:
        logger.info(f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, "
                     f"mean={df[col].mean():.2f}")

    return df
