"""
run_pipeline.py — Orchestrateur du pipeline de clustering.
Sprint 2 — Daniel (Data Engineer)

Usage :
  python -m data.pipeline.run_pipeline              # pipeline complet
  python -m data.pipeline.run_pipeline --customers   # clients uniquement
  python -m data.pipeline.run_pipeline --producers   # producteurs uniquement
  python -m data.pipeline.run_pipeline --reset       # vide les résultats puis relance
"""

import argparse
import logging
import sys
import time

from .clustering_customers import run_customer_clustering
from .clustering_producers import run_producer_clustering
from .db import get_connection, get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def reset_clustering_data(conn):
    """Supprime tous les résultats de clustering existants."""
    cur = conn.cursor()
    cur.execute("""
        TRUNCATE customer_segments, producer_segments, clustering_runs
        RESTART IDENTITY CASCADE
    """)
    conn.commit()
    cur.close()
    logger.info("Tables de clustering vidées.")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de clustering — Marketplace Locale Intelligente"
    )
    parser.add_argument("--customers", action="store_true",
                        help="Exécuter uniquement le clustering clients.")
    parser.add_argument("--producers", action="store_true",
                        help="Exécuter uniquement le clustering producteurs.")
    parser.add_argument("--reset", action="store_true",
                        help="Vider les résultats précédents avant exécution.")
    args = parser.parse_args()

    # Si ni --customers ni --producers, on fait les deux
    run_customers = args.customers or (not args.customers and not args.producers)
    run_producers = args.producers or (not args.customers and not args.producers)

    logger.info("=" * 60)
    logger.info("Pipeline de clustering — Démarrage")
    logger.info("=" * 60)

    start = time.time()

    try:
        conn = get_connection()
        engine = get_engine()
    except Exception as e:
        logger.error(f"Impossible de se connecter à PostgreSQL : {e}")
        logger.error("Vérifiez que le conteneur est lancé : docker compose up -d")
        sys.exit(1)

    if args.reset:
        reset_clustering_data(conn)

    customer_run_id = None
    producer_run_id = None

    if run_customers:
        logger.info("-" * 40)
        logger.info("CLUSTERING CLIENTS")
        logger.info("-" * 40)
        customer_run_id = run_customer_clustering(conn, engine)

    if run_producers:
        logger.info("-" * 40)
        logger.info("CLUSTERING PRODUCTEURS")
        logger.info("-" * 40)
        producer_run_id = run_producer_clustering(conn, engine)

    conn.close()
    engine.dispose()

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info(f"Pipeline terminé en {elapsed:.1f}s")
    if customer_run_id:
        logger.info(f"  Clients    : run_id={customer_run_id}")
    if producer_run_id:
        logger.info(f"  Producteurs: run_id={producer_run_id}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
