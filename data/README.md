# Data — Marketplace Locale Intelligente

Dossier géré par **Daniel**.

## Structure

```
data/
├── schema/
│   └── schema.sql          # Schéma PostgreSQL (appliqué auto au démarrage Docker)
├── mock/
│   ├── seed.py             # Génération du mock data
│   └── requirements.txt    # Dépendances Python
├── notebooks/
│   └── 01_exploration.ipynb # Exploration et validation du mock data
└── README.md
```

## Prérequis

- Docker + Docker Compose
- Python 3.10+
- Un fichier `.env` à la racine (copier `.env.example`)

## Démarrage rapide

```bash
# 1. Configurer l'environnement
cp .env.example .env

# 2. Lancer PostgreSQL
docker compose up -d

# 3. Installer les dépendances Python
pip install -r data/mock/requirements.txt

# 4. Générer le mock data
python data/mock/seed.py

# 5. Re-générer (reset complet)
python data/mock/seed.py --reset
```

## Volumétrie du mock data

| Table        | Lignes  |
|--------------|---------|
| users        | 1 200   |
| producers    | 200     |
| products     | 2 000   |
| orders       | 5 000   |
| order_items  | ~17 000 |
| payments     | ~4 300  |

## Accès à la base (Read-Replica en prod)

En local : `localhost:5432`
En production : connexion via le Read-Replica provisionné par Yohann (DevOps).

```
Host     : localhost
Port     : 5432
Database : marketplace_db
User     : marketplace_user
```
