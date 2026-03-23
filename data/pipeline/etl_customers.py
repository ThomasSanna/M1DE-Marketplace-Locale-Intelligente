"""
etl_customers.py — Extraction des features clients pour le clustering.
Sprint 2 — Daniel (Data Engineer)

Features extraites (RFM + comportementales) :
  - recency_days           : jours depuis la dernière commande
  - frequency              : nombre de commandes
  - monetary               : montant total dépensé
  - avg_basket             : panier moyen
  - cancellation_rate      : taux d'annulation
  - days_since_registration: ancienneté du compte
  - favorite_category      : catégorie la plus achetée (métadonnée, non utilisée dans le clustering)
"""

import logging

import pandas as pd

from .db import get_engine, query_df

logger = logging.getLogger(__name__)

CUSTOMER_FEATURES_SQL = """
WITH client_orders AS (
    SELECT
        u.id                                            AS user_id,
        COUNT(DISTINCT o.id)                            AS frequency,
        COALESCE(SUM(o.total_amount), 0)                AS monetary,
        COALESCE(
            EXTRACT(DAY FROM NOW() - MAX(o.created_at)),
            EXTRACT(DAY FROM NOW() - u.created_at)
        )                                               AS recency_days,
        COALESCE(AVG(o.total_amount), 0)                AS avg_basket,
        EXTRACT(DAY FROM NOW() - u.created_at)          AS days_since_registration
    FROM users u
    LEFT JOIN orders o
        ON o.client_id = u.id
        AND o.status NOT IN ('draft', 'cancelled')
    WHERE u.role = 'client'
    GROUP BY u.id, u.created_at
),
cancellations AS (
    SELECT
        o.client_id                                     AS user_id,
        COUNT(*) FILTER (WHERE o.status = 'cancelled')::DECIMAL
            / NULLIF(COUNT(*), 0)                       AS cancellation_rate
    FROM orders o
    GROUP BY o.client_id
),
fav_category AS (
    SELECT DISTINCT ON (o.client_id)
        o.client_id                                     AS user_id,
        p.category                                      AS favorite_category
    FROM order_items oi
    JOIN orders o   ON o.id = oi.order_id
    JOIN products p ON p.id = oi.product_id
    WHERE o.status NOT IN ('draft', 'cancelled')
    GROUP BY o.client_id, p.category
    ORDER BY o.client_id, COUNT(*) DESC
)
SELECT
    co.user_id,
    co.recency_days,
    co.frequency,
    co.monetary,
    co.avg_basket,
    co.days_since_registration,
    COALESCE(c.cancellation_rate, 0)            AS cancellation_rate,
    COALESCE(fc.favorite_category, 'autres')    AS favorite_category
FROM client_orders co
LEFT JOIN cancellations c   ON c.user_id  = co.user_id
LEFT JOIN fav_category  fc  ON fc.user_id = co.user_id
"""


def extract_customer_features(engine=None) -> pd.DataFrame:
    """Extrait les features RFM et comportementales de tous les clients.

    Returns:
        DataFrame avec colonnes : user_id, recency_days, frequency, monetary,
        avg_basket, days_since_registration, cancellation_rate, favorite_category
    """
    if engine is None:
        engine = get_engine()

    logger.info("Extraction des features clients...")
    df = query_df(CUSTOMER_FEATURES_SQL, engine)

    # Nettoyage : remplacer les NaN résiduels par 0 pour les numériques
    numeric_cols = [
        "recency_days", "frequency", "monetary",
        "avg_basket", "cancellation_rate", "days_since_registration",
    ]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Conversion en types appropriés
    df["recency_days"] = df["recency_days"].astype(int)
    df["frequency"] = df["frequency"].astype(int)
    df["days_since_registration"] = df["days_since_registration"].astype(int)

    logger.info(f"  {len(df)} clients extraits")
    for col in numeric_cols:
        logger.info(f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, "
                     f"mean={df[col].mean():.2f}")

    return df
