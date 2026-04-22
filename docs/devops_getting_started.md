# Demarrage DevOps (Sprint 1)

Ce guide explique comment lancer localement la base Sprint 1 cote DevOps.

## Prerequis
- Docker Desktop (ou Docker Engine + Docker Compose)
- Python 3.11+
- Git

## 1. Initialiser l'environnement
```powershell
Copy-Item .env.example .env
```

## 2. Lancer la stack locale
```powershell
docker compose up --build -d
```

Services exposes :
- API backend : `http://localhost:8000`
- Documentation API : `http://localhost:8000/docs`
- Frontend : `http://localhost:3000`
- PostgreSQL : `localhost:5432`

## 3. Verifier l'etat des conteneurs
```powershell
docker compose ps
docker compose logs backend --tail=100
```

## 4. Executer les tests backend
```powershell
cd backend
python -m pip install -r requirements.txt
pytest -q
```

## 5. Arreter l'environnement
```powershell
docker compose down
```

## Notes CI / GitHub
Le workflow `.github/workflows/ci.yml` lance :
1. Installation des dependances backend
2. Verification syntaxique Python
3. Smoke test d'import FastAPI
4. Tests unitaires `pytest`
5. Build Docker de l'image backend
