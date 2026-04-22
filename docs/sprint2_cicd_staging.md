# Sprint 2 - Pipeline CI/CD vers Staging

Ce document definit la mise en place du pipeline de deploiement staging pour le Sprint 2.

## Objectif
Automatiser le flux suivant apres merge/push sur `dev`:
1. Build des images backend/frontend
2. Push dans GHCR
3. Deploiement sur un serveur cloud staging
4. Healthcheck post-deploiement

## Fichiers utilises
- `.github/workflows/deploy-staging.yml`
- `docker-compose.staging.yml`
- `data/schema/schema.sql`

## Secrets GitHub requis
Configurer ces secrets dans le repo (Settings > Secrets and variables > Actions):
- `STAGING_HOST`: IP ou DNS du serveur staging
- `STAGING_USER`: utilisateur SSH
- `STAGING_SSH_KEY`: cle privee SSH (format OpenSSH)
- `STAGING_PORT`: port SSH (22 si non modifie)
- `STAGING_APP_DIR`: dossier de deploiement distant (ex: `/opt/marketplace`)
- `STAGING_ENV_FILE`: contenu complet du fichier `.env` staging (multi-lignes)
- `GHCR_USERNAME`: utilisateur/compte autorise a pull sur GHCR
- `GHCR_TOKEN`: token GHCR (read:packages minimum)
- `STAGING_HEALTHCHECK_URL` (optionnel): URL verifiee apres deploiement (ex: `https://staging.example.com/api/v1/health`)

## Variables a mettre dans STAGING_ENV_FILE
Exemple minimal:
```env
POSTGRES_DB=marketplace_db
POSTGRES_USER=marketplace_user
POSTGRES_PASSWORD=change_me_staging
POSTGRES_PORT=5432
SECRET_KEY=change_me_super_secret
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## Workflow de deploiement
Trigger:
- fermeture de PR sur `dev` (deploiement uniquement si PR mergee)
- execution manuelle (`workflow_dispatch`)

Etapes:
1. Build + push de 2 images versionnees par SHA
2. Copie de `docker-compose.staging.yml` et `schema.sql` vers le serveur
3. Creation/maj de `.env` sur le serveur
4. `docker login ghcr.io`
5. `docker compose pull` puis `docker compose up -d --remove-orphans`
6. Healthcheck optionnel

## Pre-requis serveur staging
- Docker + Docker Compose plugin installes
- Acces internet vers `ghcr.io`
- utilisateur SSH autorise a executer docker
- ports exposes:
  - `3000` (frontend)
  - `8000` (backend)
  - `5432` (postgres, si conserve expose)

## Rollback rapide
Se connecter au serveur staging et redeployer une image precedente:
```bash
cd /opt/marketplace
export BACKEND_IMAGE=ghcr.io/<org>/<repo>/backend:<ancien_sha>
export FRONTEND_IMAGE=ghcr.io/<org>/<repo>/frontend:<ancien_sha>
docker compose -f docker-compose.staging.yml up -d
```

## Points d'attention
- Verifier que `GHCR_TOKEN` a bien l'autorisation de lecture de packages.
- Si le healthcheck echoue, investiguer:
  - `docker compose -f docker-compose.staging.yml ps`
  - `docker compose -f docker-compose.staging.yml logs backend --tail=200`
  - `docker compose -f docker-compose.staging.yml logs frontend --tail=200`
