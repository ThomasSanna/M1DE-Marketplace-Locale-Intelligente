# Sprint 4 - Ajustement du scaling Kubernetes

## Objectif
Ajuster le scaling Kubernetes selon les resultats de charge Sprint 4 afin d'optimiser le compromis performance/cout tout en respectant les objectifs SRE.

## Livrables
- Manifests Kubernetes ajoutes dans `k8s/`:
  - `namespace.yaml`
  - `backend-configmap.yaml`
  - `backend-secret.example.yaml`
  - `backend-deployment.yaml`
  - `backend-service.yaml`
  - `backend-compat-service.yaml`
  - `backend-hpa.yaml`
  - `frontend-deployment.yaml`
  - `frontend-service.yaml`
  - `kustomization.yaml`

## Decisions de scaling (backend)
Sur la base des tests k6 (smoke, nominal, stress):
1. **Replicas de base**
- `replicas: 2` sur le backend pour absorber une charge normale sans cold-start.

2. **HPA backend**
- `minReplicas: 2`
- `maxReplicas: 6`
- cibles:
  - CPU `averageUtilization: 65`
  - memoire `averageUtilization: 75`

3. **Comportement HPA**
- Scale-up rapide:
  - `+100%` max par minute.
- Scale-down plus prudent:
  - fenetre de stabilisation `300s`
  - `-30%` max par minute.

Ce comportement evite l'effet "yoyo" tout en reagissant vite en pic.

## Ressources backend
- requests:
  - CPU `250m`
  - RAM `256Mi`
- limits:
  - CPU `1000m`
  - RAM `1Gi`

## Ressources frontend
- replicas: `2`
- requests:
  - CPU `100m`
  - RAM `128Mi`
- limits:
  - CPU `500m`
  - RAM `512Mi`

## Application des manifests
Prerequis cluster:
- metrics-server installe (obligatoire pour HPA CPU/memoire).
- acces image GHCR configure.

Commande:
```bash
kubectl create namespace marketplace-staging
kubectl -n marketplace-staging create secret generic marketplace-backend-secret \
  --from-literal=POSTGRES_USER=marketplace_user \
  --from-literal=POSTGRES_PASSWORD=changeme \
  --from-literal=SECRET_KEY=ta_super_cle
kubectl apply -k k8s
```

Note:
- `backend-secret.example.yaml` est un template documente, a ne pas appliquer tel quel en environnement reel.
- `backend-compat-service.yaml` ajoute un alias DNS `backend` pour la compatibilite avec `frontend/nginx.conf` (proxy `http://backend:8000`).

## Verification
```bash
kubectl -n marketplace-staging get pods
kubectl -n marketplace-staging get deploy
kubectl -n marketplace-staging get svc
kubectl -n marketplace-staging get hpa
kubectl -n marketplace-staging describe hpa marketplace-backend-hpa
```

Pendant un test k6:
```bash
kubectl -n marketplace-staging get hpa -w
kubectl -n marketplace-staging get pods -w
kubectl -n marketplace-staging top pods
```

## Resultats observes (validation)
Execution reelle sur Minikube:
1. Etat stable avant charge:
- backend `2/2` pods `Running`
- frontend `2/2` pods `Running`
- HPA backend actif (`min=2`, `max=6`)

2. Pendant charge k6:
- HPA observe:
  - `cpu: 84%/65%` puis `cpu: 163%/65%`
  - `REPLICAS: 2 -> 3 -> 5`
- Pods backend observes:
  - creation dynamique de nouveaux pods (`Pending` -> `ContainerCreating` -> `Running`)

3. Apres charge:
- HPA observe:
  - baisse CPU a `2%/65%`
  - `REPLICAS: 5 -> 3 -> 2`
- Le retour a 2 est progressif grace a `stabilizationWindowSeconds: 300` (anti-yoyo).

## Lecture des sorties kubectl
- `TARGETS cpu: X/65%`: charge CPU actuelle (X) comparee a la cible HPA (65%).
- `TARGETS memory: Y/75%`: charge memoire actuelle (Y) comparee a la cible HPA (75%).
- `REPLICAS`: nombre de pods backend actuellement demandes par le HPA.
- `MINPODS/MAXPODS`: bornes de scaling autorisees (`2..6`).

Definition rapide:
- Un pod = une instance d'execution de l'application (conteneur).
- Si charge > cible, Kubernetes ajoute des pods.
- Si charge redescend, Kubernetes retire des pods pour limiter le cout.

## Criteres de validation
1. Le backend scale entre 2 et 6 replicas selon la charge.
2. Le scale-up se declenche sur pic soutenu.
3. Le scale-down est progressif apres retour a la normale.
4. Les indicateurs SRE restent dans des bornes acceptables (latence/erreurs).
