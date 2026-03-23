# Data — Marketplace Locale Intelligente

Dossier géré par **Daniel**.

## Structure

```
data/
├── schema/
│   ├── schema.sql                      # Schéma PostgreSQL (Sprint 1)
│   └── 002_clustering_tables.sql       # Tables de clustering (Sprint 2)
├── mock/
│   ├── seed.py                         # Génération du mock data
│   └── requirements.txt                # Dépendances Python
├── pipeline/
│   ├── db.py                           # Utilitaires de connexion DB
│   ├── etl_customers.py                # Extraction features clients (RFM)
│   ├── etl_producers.py                # Extraction features producteurs
│   ├── clustering_customers.py         # K-Means segmentation clients
│   ├── clustering_producers.py         # K-Means segmentation producteurs
│   └── run_pipeline.py                 # Orchestrateur du pipeline
├── notebooks/
│   ├── 01_exploration.ipynb            # Exploration du mock data (Sprint 1)
│   └── 02_clustering_analysis.ipynb    # Analyse des résultats de clustering (Sprint 2)
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

## Pipeline de clustering (Sprint 2)

```bash
# Exécuter le pipeline complet (clients + producteurs)
python -m data.pipeline.run_pipeline

# Clients uniquement
python -m data.pipeline.run_pipeline --customers

# Producteurs uniquement
python -m data.pipeline.run_pipeline --producers

# Reset des résultats puis relance
python -m data.pipeline.run_pipeline --reset
```

### Fonctionnement

1. **ETL** — Extraction des features depuis PostgreSQL (requêtes SQL avec CTEs)
   - Clients : RFM (Recency, Frequency, Monetary) + comportement (panier moyen, taux annulation)
   - Producteurs : activité (nb produits, diversité) + performance (CA, commandes)
2. **Clustering** — K-Means avec StandardScaler
   - Recherche automatique du K optimal (score silhouette)
   - Labeling automatique des clusters par analyse des centroïdes
3. **Stockage** — Résultats écrits dans `customer_segments` / `producer_segments`
   - Chaque exécution tracée dans `clustering_runs` (reproductibilité)
   - Vues `v_current_customer_segments` et `v_current_producer_segments` pour consommation

### Consommation des résultats

- **API** (Thomas) : `SELECT * FROM v_current_customer_segments` pour `GET /api/v1/data/clustering/customers`
- **Power BI** (Manon) : DirectQuery sur les vues `v_current_*`
- **Notebook** : `02_clustering_analysis.ipynb` pour visualisation

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
