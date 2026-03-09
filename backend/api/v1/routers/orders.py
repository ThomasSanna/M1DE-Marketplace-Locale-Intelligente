from fastapi import APIRouter

router = APIRouter(tags=["Orders & Payments"])

@router.post("/orders")
def create_order():
    """Transforme le panier Front-end en Commande (Brouillon)."""
    return {"message": "Order created (Draft)"}

@router.get("/orders")
def list_orders():
    """[Auth] Récupération de l'historique des commandes d'un utilisateur."""
    return {"message": "List of user orders"}

@router.get("/orders/{order_id}")
def get_order(order_id: int):
    """Détail d'une commande."""
    return {"order_id": order_id, "message": "Order details"}

@router.post("/payments")
def simulate_payment():
    """Simulateur de Paiement. Valide la commande et prélève les stocks définitivement."""
    return {"message": "Payment simulated"}

@router.patch("/orders/{order_id}/status")
def update_order_status(order_id: int):
    """[Auth Producer] Mise à jour d'expédition (Validée -> Expédiée)."""
    return {"order_id": order_id, "message": "Order status updated"}
