import os
import sys
from sqlalchemy import text
from database import engine

# Remonter d'un dossier pour accéder à 'data/schema/schema.sql'
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schema", "schema.sql")

def init_db():
    print(f"Loading schema from: {SCHEMA_PATH}")
    if not os.path.exists(SCHEMA_PATH):
        print("Erreur: Le fichier schema.sql n'a pas été trouvé.")
        sys.exit(1)
        
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    try:
        with engine.connect() as conn:
            # Exécuter le script SQL brut
            # text() enveloppe la commande pour SQLAlchemy 2.0
            conn.execute(text(sql_script))
            conn.commit()
            print("Succès: La base de données a été initialisée avec le schéma !")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")

if __name__ == "__main__":
    init_db()
