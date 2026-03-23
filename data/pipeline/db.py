"""
db.py — Utilitaires de connexion à la base de données.
Centralise la logique de connexion pour tous les scripts du pipeline.
"""

import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Charge le .env depuis la racine du projet
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_connection():
    """Retourne une connexion psycopg2 vers PostgreSQL."""
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
    )


def get_engine():
    """Retourne un engine SQLAlchemy pour pandas."""
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", 5432)
    db = os.getenv("POSTGRES_DB")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")


def query_df(sql: str, engine=None) -> pd.DataFrame:
    """Exécute une requête SQL et retourne un DataFrame pandas."""
    if engine is None:
        engine = get_engine()
    return pd.read_sql(sql, engine)
