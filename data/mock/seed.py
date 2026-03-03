"""
seed.py — Génération du mock data pour la Marketplace Locale Intelligente
Sprint 1 — Data Engineer : Daniel

Volumétrie cible :
  - 200 producteurs
  - 1 000 clients
  - 2 000 produits
  - 5 000 commandes (avec lignes)
  - 5 000 paiements (5% d'échecs simulés)
"""

import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker("fr_FR")
random.seed(42)

# ---------------------------------------------------------------------------
# Connexion
# ---------------------------------------------------------------------------

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="localhost",
    port=os.getenv("POSTGRES_PORT", 5432),
)
cur = conn.cursor()

# ---------------------------------------------------------------------------
# Constantes métier
# ---------------------------------------------------------------------------

REGIONS = [
    "Corse-du-Sud", "Haute-Corse", "Provence-Alpes-Côte d'Azur",
    "Occitanie", "Nouvelle-Aquitaine", "Bretagne", "Pays de la Loire",
]

CATEGORIES = [
    "fruits", "legumes", "viandes", "poissons",
    "produits_laitiers", "epicerie", "boissons", "autres",
]

UNITS = ["kg", "g", "litre", "piece", "bouquet", "boite"]

# Prix moyens par catégorie (min, max) en euros
PRICE_RANGES = {
    "fruits":            (0.80, 6.00),
    "legumes":           (0.50, 4.00),
    "viandes":           (8.00, 35.00),
    "poissons":          (6.00, 28.00),
    "produits_laitiers": (1.50, 12.00),
    "epicerie":          (1.00, 20.00),
    "boissons":          (2.00, 15.00),
    "autres":            (1.00, 10.00),
}

ORDER_STATUSES = ["draft", "confirmed", "shipped", "delivered", "cancelled"]
# Pondération réaliste : majorité confirmée/livrée pour des données analytiques riches
STATUS_WEIGHTS  = [0.05, 0.15, 0.15, 0.55, 0.10]

PAYMENT_ERROR_RATE = 0.05  # 5% simulé volontairement (cf. architecture docs)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_date(start_days_ago: int, end_days_ago: int = 0) -> datetime:
    delta = random.randint(end_days_ago, start_days_ago)
    return datetime.now(timezone.utc) - timedelta(days=delta)


def fake_password_hash() -> str:
    return "$2b$12$" + fake.sha256()[:53]


# ---------------------------------------------------------------------------
# 1. Utilisateurs (clients + producteurs)
# ---------------------------------------------------------------------------

print("→ Génération des utilisateurs...")

producer_ids = []
client_ids   = []

users_data = []

for _ in range(200):   # producteurs
    uid = str(uuid.uuid4())
    producer_ids.append(uid)
    created = rand_date(365, 30)
    users_data.append((
        uid, fake.unique.email(), fake_password_hash(), "producer",
        fake.first_name(), fake.last_name(), fake.phone_number(),
        created, created, None,
    ))

for _ in range(1000):  # clients
    uid = str(uuid.uuid4())
    client_ids.append(uid)
    created    = rand_date(365, 0)
    last_login = created + timedelta(days=random.randint(0, 30)) if random.random() > 0.1 else None
    users_data.append((
        uid, fake.unique.email(), fake_password_hash(), "client",
        fake.first_name(), fake.last_name(), fake.phone_number(),
        created, created, last_login,
    ))

cur.executemany(
    """
    INSERT INTO users (id, email, password_hash, role, first_name, last_name,
                       phone, created_at, updated_at, last_login_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    users_data,
)
print(f"  ✓ {len(users_data)} utilisateurs insérés")

# ---------------------------------------------------------------------------
# 2. Producteurs (profils étendus)
# ---------------------------------------------------------------------------

print("→ Génération des profils producteurs...")

producers_data = []
producer_profile_ids = []  # UUID du profil producer (≠ user_id)

for user_id in producer_ids:
    pid    = str(uuid.uuid4())
    region = random.choice(REGIONS)
    producer_profile_ids.append(pid)
    producers_data.append((
        pid, user_id,
        fake.company(),
        fake.city(), region,
        float(fake.latitude()), float(fake.longitude()),
        fake.text(max_nb_chars=200),
        rand_date(365, 30),
    ))

cur.executemany(
    """
    INSERT INTO producers (id, user_id, farm_name, location_city, location_region,
                           location_lat, location_lng, description, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    producers_data,
)
print(f"  ✓ {len(producers_data)} profils producteurs insérés")

# ---------------------------------------------------------------------------
# 3. Produits
# ---------------------------------------------------------------------------

print("→ Génération des produits...")

products_data = []
product_ids   = []

for _ in range(2000):
    pid      = str(uuid.uuid4())
    category = random.choice(CATEGORIES)
    p_min, p_max = PRICE_RANGES[category]
    producer_pid = random.choice(producer_profile_ids)
    created  = rand_date(300, 1)

    product_ids.append(pid)
    products_data.append((
        pid, producer_pid,
        fake.word().capitalize() + " " + fake.word(),
        fake.text(max_nb_chars=100),
        category,
        round(random.uniform(p_min, p_max), 2),
        round(random.uniform(0, 200), 3),
        random.choice(UNITS),
        True,
        created, created,
    ))

cur.executemany(
    """
    INSERT INTO products (id, producer_id, name, description, category,
                          price, stock_quantity, unit, is_active, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    products_data,
)
print(f"  ✓ {len(products_data)} produits insérés")

# ---------------------------------------------------------------------------
# 4. Commandes + lignes de commande
# ---------------------------------------------------------------------------

print("→ Génération des commandes et lignes...")

orders_data      = []
order_items_data = []

for _ in range(5000):
    oid        = str(uuid.uuid4())
    client_id  = random.choice(client_ids)
    status     = random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS)[0]
    created    = rand_date(180, 0)

    confirmed_at = None
    delivered_at = None
    if status in ("confirmed", "shipped", "delivered"):
        confirmed_at = created + timedelta(hours=random.randint(1, 24))
    if status == "delivered":
        delivered_at = confirmed_at + timedelta(days=random.randint(1, 7))

    # Lignes de commande (1 à 6 produits par commande)
    nb_items   = random.randint(1, 6)
    items      = random.sample(product_ids, k=min(nb_items, len(product_ids)))
    total      = Decimal("0.00")

    for product_id in items:
        # Retrouver le prix du produit depuis products_data
        prod = next(p for p in products_data if p[0] == product_id)
        price    = Decimal(str(prod[5]))
        qty      = round(random.uniform(0.5, 10.0), 3)
        total   += price * Decimal(str(qty))

        order_items_data.append((
            str(uuid.uuid4()), oid, product_id,
            qty, float(price),
        ))

    orders_data.append((
        oid, client_id, status, float(total.quantize(Decimal("0.01"))),
        created, created, confirmed_at, delivered_at,
    ))

cur.executemany(
    """
    INSERT INTO orders (id, client_id, status, total_amount,
                        created_at, updated_at, confirmed_at, delivered_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """,
    orders_data,
)
cur.executemany(
    """
    INSERT INTO order_items (id, order_id, product_id, quantity, unit_price_snapshot)
    VALUES (%s, %s, %s, %s, %s)
    """,
    order_items_data,
)
print(f"  ✓ {len(orders_data)} commandes insérées ({len(order_items_data)} lignes)")

# ---------------------------------------------------------------------------
# 5. Paiements (5% d'erreurs simulées)
# ---------------------------------------------------------------------------

print("→ Génération des paiements...")

payments_data = []

for order in orders_data:
    oid, _, status, total_amount, created_at = order[0], order[1], order[2], order[3], order[4]

    # Seules les commandes non-draft et non-annulées ont un paiement
    if status in ("draft", "cancelled"):
        continue

    is_error       = random.random() < PAYMENT_ERROR_RATE
    payment_status = "failed" if is_error else "success"

    payments_data.append((
        str(uuid.uuid4()), oid, total_amount,
        payment_status, is_error,
        created_at + timedelta(minutes=random.randint(1, 30)),
    ))

cur.executemany(
    """
    INSERT INTO payments (id, order_id, amount, status, is_simulated_error, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """,
    payments_data,
)
print(f"  ✓ {len(payments_data)} paiements insérés "
      f"({sum(1 for p in payments_data if p[3] == 'failed')} échecs simulés)")

# ---------------------------------------------------------------------------
# Commit & fermeture
# ---------------------------------------------------------------------------

conn.commit()
cur.close()
conn.close()

print("\n✅ Mock data généré avec succès.")
