from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/")
def list_products():
    """Liste les produits de la marketplace (avec pagination et filtres géographiques/prix)."""
    return {"message": "List of all products"}

@router.get("/{product_id}")
def get_product(product_id: int):
    """Récupère les détails spécifiques d'un produit."""
    return {"product_id": product_id, "message": "Product details"}

@router.post("/")
def create_product():
    """[Auth Producer] Ajoute un nouveau produit au catalogue."""
    return {"message": "Product created"}

@router.put("/{product_id}")
def update_product(product_id: int):
    """[Auth Producer] Modifie un produit existant ou ajuste le stock."""
    return {"product_id": product_id, "message": "Product updated"}

@router.delete("/{product_id}")
def delete_product(product_id: int):
    """[Auth Producer] Supprime/Désactive un produit."""
    return {"product_id": product_id, "message": "Product deleted"}
