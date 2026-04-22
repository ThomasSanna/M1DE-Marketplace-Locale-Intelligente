"""
etl_producers.py — Extraction des features producteurs pour le clustering.
Sprint 2 — Daniel (Data Engineer)

Features extraites :
  - n_products       : nombre de produits au catalogue
  - n_categories     : diversité (nombre de catégories distinctes)
  - total_revenue    : chiffre d'affaires total
  - n_orders_received: nombre de commandes reçues
  - avg_order_value  : valeur moyenne par commande
  - days_active      : ancienneté du producteur
  - location_region  : région (métadonnée, non utilisée dans le clustering)
"""

import logging

import pandas as pd

from .db import get_engine, query_df

logger = logging.getLogger(__name__)

PRODUCER_FEATURES_SQL = """
SELECT
    pr.id                                               AS producer_id,
    pr.location_region,
    COUNT(DISTINCT p.id)                                AS n_products,
    COUNT(DISTINCT p.category)                          AS n_categories,
    COALESCE(SUM(oi.quantity * oi.unit_price_snapshot), 0) AS total_revenue,
    COUNT(DISTINCT o.id)                                AS n_orders_received,
    CASE
        WHEN COUNT(DISTINCT o.id) > 0
        THEN SUM(oi.quantity * oi.unit_price_snapshot) / COUNT(DISTINCT o.id)
        ELSE 0
    END                                                 AS avg_order_value,
    EXTRACT(DAY FROM NOW() - pr.created_at)             AS days_active
FROM producers pr
LEFT JOIN products p    ON p.producer_id = pr.id
LEFT JOIN order_items oi ON oi.product_id = p.id
LEFT JOIN orders o      ON o.id = oi.order_id
                        AND o.status IN ('confirmed', 'shipped', 'delivered')
GROUP BY pr.id, pr.location_region, pr.created_at
"""


def extract_producer_features(engine=None) -> pd.DataFrame:
    """Extrait les features de tous les producteurs.

    Returns:
        DataFrame avec colonnes : producer_id, location_region, n_products,
        n_categories, total_revenue, n_orders_received, avg_order_value, days_active
    """
    if engine is None:
        engine = get_engine()

    logger.info("Extraction des features producteurs...")
    df = query_df(PRODUCER_FEATURES_SQL, engine)

    numeric_cols = [
        "n_products", "n_categories", "total_revenue",
        "n_orders_received", "avg_order_value", "days_active",
    ]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    df["n_products"] = df["n_products"].astype(int)
    df["n_categories"] = df["n_categories"].astype(int)
    df["n_orders_received"] = df["n_orders_received"].astype(int)
    df["days_active"] = df["days_active"].astype(int)

    logger.info(f"  {len(df)} producteurs extraits")
    for col in numeric_cols:
        logger.info(f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, "
                     f"mean={df[col].mean():.2f}")

    return df
