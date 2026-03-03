from fastapi import APIRouter

router = APIRouter(prefix="/data", tags=["Data & Analytics"])

@router.get("/sales-metrics")
def get_sales_metrics():
    """Renvoie les ventes totales agrégées, le panier moyen."""
    return {"message": "Sales metrics"}

@router.get("/clustering/customers")
def get_customers_clustering():
    """Renvoie le segment 'Clientèle' calculé en asynchrone par les scripts."""
    return {"message": "Customers clustering segments"}

@router.get("/anomalies")
def get_anomalies():
    """Renvoie les transactions flaguées comme potentiellement frauduleuses."""
    return {"message": "Anomalies detection"}
