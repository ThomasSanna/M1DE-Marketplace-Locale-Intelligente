"""
enrich_exports.py — Enrichit les exports CSV avec des dimensions demandees par Manon
                    (dashboard Power BI) sans toucher au schema de la DB.

Colonnes ajoutees :
  users.csv      : gender, birth_date, csp, postal_code, city
  producers.csv  : postal_code (en complement de location_city)
  products.csv   : wholesale_price
  orders.csv     : satisfaction (1-5, NULL si non livree)

Pre-requis : les CSV de base doivent etre dans data/exports/
             (generes via `psql \\COPY`).

Usage :
  python data/mock/enrich_exports.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

fake = Faker("fr_FR")
random.seed(42)
Faker.seed(42)

EXPORTS_DIR = Path(__file__).resolve().parents[1] / "exports"

CSP_INSEE = [
    "Agriculteurs exploitants",
    "Artisans, commercants, chefs d'entreprise",
    "Cadres et professions intellectuelles superieures",
    "Professions intermediaires",
    "Employes",
    "Ouvriers",
    "Retraites",
    "Autres personnes sans activite professionnelle",
]
CSP_WEIGHTS = [2, 7, 17, 26, 28, 12, 5, 3]


def random_birth_date() -> date:
    today = date(2026, 4, 14)
    age_days = random.randint(18 * 365, 75 * 365)
    return today - timedelta(days=age_days)


def enrich_users():
    src = EXPORTS_DIR / "users.csv"
    with src.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    new_cols = ["gender", "birth_date", "csp", "postal_code", "city"]
    for row in rows:
        row["gender"] = random.choice(["M", "F"])
        row["birth_date"] = random_birth_date().isoformat()
        row["csp"] = random.choices(CSP_INSEE, weights=CSP_WEIGHTS, k=1)[0]
        row["postal_code"] = fake.postcode()
        row["city"] = fake.city()

    with src.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] users.csv enrichi : +{len(new_cols)} colonnes ({len(rows)} lignes)")


def enrich_producers():
    src = EXPORTS_DIR / "producers.csv"
    with src.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        row["postal_code"] = fake.postcode()

    with src.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] producers.csv enrichi : +1 colonne ({len(rows)} lignes)")


def enrich_products():
    src = EXPORTS_DIR / "products.csv"
    with src.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        price = float(row["price"])
        ratio = random.uniform(0.50, 0.75)
        row["wholesale_price"] = f"{round(price * ratio, 2)}"

    with src.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] products.csv enrichi : +1 colonne ({len(rows)} lignes)")


def enrich_orders():
    src = EXPORTS_DIR / "orders.csv"
    with src.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    n_rated = 0
    for row in rows:
        if row["status"] == "delivered":
            row["satisfaction"] = random.choices(
                [1, 2, 3, 4, 5], weights=[3, 6, 15, 40, 36], k=1
            )[0]
            n_rated += 1
        else:
            row["satisfaction"] = ""

    with src.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"[OK] orders.csv enrichi : +1 colonne "
        f"({len(rows)} lignes, {n_rated} notees)"
    )


def main():
    if not EXPORTS_DIR.exists():
        raise SystemExit(
            f"[ERREUR] {EXPORTS_DIR} n'existe pas. "
            "Genere d'abord les CSV de base avec les commandes psql \\COPY."
        )
    enrich_users()
    enrich_producers()
    enrich_products()
    enrich_orders()
    print("\nPret pour Manon. Pense a regenerer le zip.")


if __name__ == "__main__":
    main()
