from fastapi import APIRouter

router = APIRouter(tags=["Auth & Producers"])

@router.post("/auth/register")
def register():
    """Inscription d'un nouveau client ou producteur."""
    return {"message": "User registered"}

@router.post("/auth/login")
def login():
    """Authentification (Retourne un JWT Token)."""
    return {"message": "JWT Token"}

@router.get("/users/me")
def get_current_user():
    """Récupération du profil."""
    return {"message": "User profile"}

@router.get("/producers")
def list_producers():
    """Liste tous les producteurs locaux."""
    return {"message": "List of producers"}

@router.get("/producers/{producer_id}/products")
def get_producer_products(producer_id: int):
    """Récupère la vitrine/boutique d'un producteur spécifique."""
    return {"producer_id": producer_id, "message": "Producer products"}
