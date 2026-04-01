from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
import schemas

router = APIRouter(prefix="/data", tags=["Data & Analytics"])


_SALES_METRICS_SQL = """
SELECT
    COALESCE(SUM(v.revenue), 0)::double precision AS total_revenue,
    COALESCE(
        SUM(v.revenue) / NULLIF(SUM(v.nb_orders), 0),
        0
    )::double precision AS average_basket,
    COALESCE(SUM(v.nb_orders), 0)::INTEGER AS total_orders
FROM v_sales_summary v
"""

_LATEST_CUSTOMER_RUN_SQL = """
SELECT
    id AS run_id,
    n_clusters
FROM clustering_runs
WHERE run_type = 'customer' AND status = 'success'
ORDER BY finished_at DESC NULLS LAST, id DESC
LIMIT 1
"""

_CUSTOMER_SEGMENTS_COUNT_SQL = """
SELECT COUNT(*)::INTEGER AS segments_count
FROM customer_segments
WHERE run_id = :run_id
"""

_CUSTOMER_SEGMENTS_SQL = """
SELECT
    cs.user_id,
    cs.cluster_id,
    cs.cluster_label,
    cs.recency_days,
    cs.frequency,
    cs.monetary::double precision AS monetary,
    cs.avg_basket::double precision AS avg_basket,
    cs.favorite_category,
    cs.cancellation_rate::double precision AS cancellation_rate,
    cs.days_since_registration,
    u.email,
    u.first_name,
    u.last_name
FROM customer_segments cs
JOIN users u ON u.id = cs.user_id
WHERE cs.run_id = :run_id
ORDER BY cs.cluster_id ASC, cs.user_id ASC
LIMIT :limit
"""

_ANOMALIES_COUNT_SQL = """
SELECT COUNT(*)::INTEGER AS total_anomalies
FROM payments p
WHERE p.status = 'failed' OR p.is_simulated_error = TRUE
"""

_ANOMALIES_SQL = """
SELECT
    p.id AS payment_id,
    p.order_id,
    o.client_id,
    u.email AS client_email,
    p.amount::double precision AS amount,
    p.status::text AS payment_status,
    o.status::text AS order_status,
    p.is_simulated_error,
    p.created_at AS detected_at,
    CASE
        WHEN p.is_simulated_error THEN 'simulated_payment_error'
        ELSE 'payment_failure'
    END AS anomaly_type
FROM payments p
JOIN orders o ON o.id = p.order_id
LEFT JOIN users u ON u.id = o.client_id
WHERE p.status = 'failed' OR p.is_simulated_error = TRUE
ORDER BY p.created_at DESC
LIMIT :limit
"""


def _analytics_source_unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail="Analytics data source unavailable. Ensure analytical schema objects are initialized.",
    )


@router.get("/sales-metrics", response_model=schemas.SalesMetricsResponse)
def get_sales_metrics(db: Session = Depends(get_db)):
    """Renvoie les ventes totales agrégées et le panier moyen."""
    try:
        metrics = db.execute(text(_SALES_METRICS_SQL)).mappings().first()
    except SQLAlchemyError as exc:
        raise _analytics_source_unavailable() from exc

    if metrics is None:
        return schemas.SalesMetricsResponse(total_revenue=0.0, average_basket=0.0, total_orders=0)

    return schemas.SalesMetricsResponse(
        total_revenue=float(metrics.get("total_revenue") or 0),
        average_basket=float(metrics.get("average_basket") or 0),
        total_orders=int(metrics.get("total_orders") or 0),
    )


@router.get("/clustering/customers", response_model=schemas.CustomerClusteringResponse)
def get_customers_clustering(
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Renvoie les segments clients de la dernière exécution de clustering réussie."""
    try:
        latest_run = db.execute(text(_LATEST_CUSTOMER_RUN_SQL)).mappings().first()
    except SQLAlchemyError as exc:
        raise _analytics_source_unavailable() from exc

    if latest_run is None:
        return schemas.CustomerClusteringResponse()

    try:
        count_row = db.execute(
            text(_CUSTOMER_SEGMENTS_COUNT_SQL),
            {"run_id": latest_run["run_id"]},
        ).mappings().first()
        segment_rows = db.execute(
            text(_CUSTOMER_SEGMENTS_SQL),
            {"run_id": latest_run["run_id"], "limit": limit},
        ).mappings().all()
    except SQLAlchemyError as exc:
        raise _analytics_source_unavailable() from exc

    segments = [schemas.CustomerClusterSegment(**row) for row in segment_rows]
    return schemas.CustomerClusteringResponse(
        run_id=int(latest_run["run_id"]),
        n_clusters=int(latest_run["n_clusters"] or 0),
        segments_count=int((count_row or {}).get("segments_count") or 0),
        segments=segments,
    )


@router.get("/anomalies", response_model=schemas.AnomaliesResponse)
def get_anomalies(
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Renvoie les paiements en échec ou flagués comme anomalies."""
    try:
        count_row = db.execute(text(_ANOMALIES_COUNT_SQL)).mappings().first()
        anomaly_rows = db.execute(text(_ANOMALIES_SQL), {"limit": limit}).mappings().all()
    except SQLAlchemyError as exc:
        raise _analytics_source_unavailable() from exc

    anomalies = [schemas.AnomalyItem(**row) for row in anomaly_rows]
    return schemas.AnomaliesResponse(
        total_anomalies=int((count_row or {}).get("total_anomalies") or 0),
        anomalies=anomalies,
    )
