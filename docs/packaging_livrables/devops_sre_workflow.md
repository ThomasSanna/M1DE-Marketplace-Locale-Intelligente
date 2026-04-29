# Workflow DevOps et Stratégie SRE

L'assurance qualité logicielle et la fiabilité du déploiement sont garanties par Yohann (DevOps/SRE) avec le soutien de l'ensemble de l'équipe (Thomas, Mohamed).

## 1. GitFlow et Stratégie de Collaboration Git

Afin de travailler sans conflit et de garantir un code sain, nous appliquerons une stratégie de branching stricte **GitFlow** modifiée.
* `main` : Reflète l'état de la Production applicative. Déployé sur Kubernetes en Prod.
* `develop` : Reflète le code de test actuel. Déployé sur l'environnement Staging.
* `feature/XXX` : Branche de travail (ex: `feature/cart-management`).
* `hotfix/XXX` : Seule branche acceptée à bifurquer directement depuis `main` pour un correctif critique.

**Conditions Absolues des Pull Requests (PR) :**
1. Chaque PR d'une feature vers `develop` doit être approuvée par **au moins 1 autre développeur** (Code Review systématique).
2. Le pipeline CI **doit obligatoirement passer au vert** (Tests unitaires valides, Build Docker fonctionnel) pour autoriser le bouton de merge ("Branch protection rules" sur GitHub/GitLab).

---

## 2. Pipeline CI/CD (Intégration et Déploiement Continus)

Le workflow `ci-cd.yml` comportera les jobs automatisés suivants :

1. **Phase de CI (sur chaque push sur une PR) :**
   * **Lint & Formatting :** Vérification de la syntaxe du code (ex: ESLint/Prettier/Flake8).
   * **Unit Tests :** Exécution de la suite de tests (Jest / PyTest).
   * **Security Scan :** Analyse des vulnérabilités des dépendances (ex: Trivy ou SonarQube).
2. **Phase de Build (sur merge vers `develop` / `main`) :**
   * Build de l'image Docker du Front-end et du Backend.
   * Push de l'image vers une Container Registry sécurisée (GitHub Packages, AWS ECR, ou Docker Hub).
3. **Phase de CD (Déploiement) :**
   * Mise à jour des manifestes Kubernetes ou du `docker-compose.yml` du serveur.
   * Redémarrage "Zero Downtime" de l'application (Rolling Update).

---

## 3. Démarche SRE (Site Reliability Engineering)

Le monitoring est centré sur l'utilisateur final pour garantir le niveau de service. Yohann définira les métriques en concertation avec Thomas (Lead Dev) et Mohamed (Product Owner Frontend).

### Nos SLIs (Service Level Indicators)
Les métriques extraites en temps réel par Prometheus :
1. **Disponibilité (Availability) :** Taux de requêtes HTTP réussies (`HTTP 200/201/300` vs `HTTP 5xx`) sur tous les endpoints critiques.
2. **Latence (Latency) :** Temps de réponse en millisecondes pour l'endpoint `POST /api/v1/orders`.
3. **Taux d'erreur métier :** Pourcentage d'échecs rencontrés sur l'endpoint de paiement final `POST /api/v1/payments`.

### Nos SLOs (Service Level Objectives) ciblés
Les promesses réalistes que l'équipe ingénierie fait au métier (aux producteurs/clients) :
* **SLO 1 :** 99.5% des requêtes vers l'API globale aboutissent avec succès (Code Http < 500) sur une période de 30 jours consécutifs.
* **SLO 2 :** 90% des appels API de création de commande s'exécutent en moins de 300 millisecondes.
* **SLO 3 :** Le service de paiement simulé ne doit jamais échouer (0 erreur technique inattendue) sur 99.9% des tentatives.

### Notre SLA (Service Level Agreement)
C'est le contrat "commercial" qui repose sur nos SLO.
* L'application s'engage sur un taux de disponibilité de **99.0%** par mois (soit env. 7,3 heures d'indisponibilité autorisées par mois maximum).

### Politique d'Error Budget 
L'Error Budget représente l'écart entre un temps de fonctionnement de 100% et notre SLO défini (0.5% d'erreur pour notre SLO 1).
* **Si le budget est positif** : Thomas et Mohamed (Développeurs) ont l'autorisation par Yohann et le CA (Continuous Approval) de déployer de nouvelles features librement (Risque accepté).
* **Si le budget est épuisé (SLO non respecté)** : **Freezing des déploiements majeurs.** Tous les membres techniques de l'équipe travaillent de concert sur des tâches de stabilité et résolution de dette technique et SRE, afin de remonter le niveau de garantie. Mohamed et Thomas ne font plus que du *bug fix* jusqu'à rétablissement du budget.

---

## 4. Orcherstration, Conteneurisation et Monitoring

* **Conteneurisation (Docker) :** Chaque brique logique (Front, Back, DB, Scripts Data) sera isolée dans un `Dockerfile` optimisé multi-stage. L'orchestration ciblée sera **Kubernetes** pour permettre de garantir nos SLO via la montée en charge automatique (HPA - Horizontal Pod Autoscaler). Si le contexte Cloud le limite, nous utiliserons `docker-compose` de façon stricte.
* **Monitoring & Observabilité :**
  * **Prometheus :** Collectera via Scraping automatique toutes les données d'application (node-exporter, cAdvisor, custom metrics).
  * **Grafana :** Lira les données depuis Prometheus pour afficher les graphes. Nous concevrons 2 Dashboards d'observabilité : un **Dashboard Système applicatif** (CPU/RAM des pods, Load HTTP), et un **Dashboard SRE** affichant explicitement le décalage avec le SLO et la consommation de l'Error Budget.
  * Les alertes seront déclenchées (ex: Discord/Slack Webhook) si le seuil critique est franchi concernant l'Error Budget.
