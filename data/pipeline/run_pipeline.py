"""
run_pipeline.py — Orchestrateur du pipeline data (clustering + anomalies).
Sprint 2-3 — Daniel (Data Engineer)

Usage :
  python -m data.pipeline.run_pipeline              # pipeline complet (clustering + anomalies)
  python -m data.pipeline.run_pipeline --customers   # clustering clients uniquement
  python -m data.pipeline.run_pipeline --producers   # clustering producteurs uniquement
  python -m data.pipeline.run_pipeline --anomalies   # détection d'anomalies uniquement
  python -m data.pipeline.run_pipeline --reset       # vide les résultats puis relance
"""

import argparse
import logging
import sys
import time

from .anomaly_detection import run_anomaly_detection
from .clustering_customers import run_customer_clustering
from .clustering_producers import run_producer_clustering
from .db import get_connection, get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def reset_data(conn):
    """Supprime tous les résultats de clustering et d'anomalies existants."""
    cur = conn.cursor()
    cur.execute("""
        TRUNCATE customer_segments, producer_segments, clustering_runs
        RESTART IDENTITY CASCADE
    """)
    cur.execute("""
        TRUNCATE anomalies, anomaly_runs
        RESTART IDENTITY CASCADE
    """)
    conn.commit()
    cur.close()
    logger.info("Tables de clustering et d'anomalies vidées.")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline data — Marketplace Locale Intelligente"
    )
    parser.add_argument("--customers", action="store_true",
                        help="Exécuter uniquement le clustering clients.")
    parser.add_argument("--producers", action="store_true",
                        help="Exécuter uniquement le clustering producteurs.")
    parser.add_argument("--anomalies", action="store_true",
                        help="Exécuter uniquement la détection d'anomalies.")
    parser.add_argument("--reset", action="store_true",
                        help="Vider les résultats précédents avant exécution.")
    args = parser.parse_args()

    # Si aucun flag spécifique, on fait tout
    run_all = not args.customers and not args.producers and not args.anomalies
    run_customers = args.customers or run_all
    run_producers = args.producers or run_all
    run_anomalies = args.anomalies or run_all

    logger.info("=" * 60)
    logger.info("Pipeline data — Démarrage")
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
        reset_data(conn)

    customer_run_id = None
    producer_run_id = None
    anomaly_run_id = None

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

    if run_anomalies:
        logger.info("-" * 40)
        logger.info("DÉTECTION D'ANOMALIES")
        logger.info("-" * 40)
        anomaly_run_id = run_anomaly_detection(conn, engine)

    conn.close()
    engine.dispose()

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info(f"Pipeline terminé en {elapsed:.1f}s")
    if customer_run_id:
        logger.info(f"  Clients    : run_id={customer_run_id}")
    if producer_run_id:
        logger.info(f"  Producteurs: run_id={producer_run_id}")
    if anomaly_run_id:
        logger.info(f"  Anomalies  : run_id={anomaly_run_id}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
