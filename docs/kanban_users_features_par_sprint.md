# Kanban - Users et Features par Sprint

Ce document est pret a etre transforme en cartes Kanban. Chaque element contient un mini resume.

## Sprint 1 - Fondations (Semaines 1 a 3)

### User Stories (Users)

1. `US1.1` En tant que visiteur, je peux creer un compte client ou producteur.
Mini resume : Lance le parcours utilisateur de base et permet l'acces aux fonctions authentifiees.

2. `US1.2` En tant qu'utilisateur connecte, je peux me connecter et recuperer mon profil.
Mini resume : Verifie le cycle d'authentification (login + profil) pour stabiliser les flux front/back.

3. `US1.3` En tant que client, je peux consulter la liste des produits et le detail d'un produit.
Mini resume : Pose le coeur de l'experience marketplace avec navigation catalogue minimale.

### Features techniques

1. `FEAT1.1` Initialisation backend + BDD PostgreSQL (schema utilisateurs/produits).
Mini resume : Etablit la base transactionnelle necessaire a toutes les evolutions suivantes.
Assigne a : `Thomas`

2. `FEAT1.2` CRUD minimal API produits + endpoints auth/utilisateur.
Mini resume : Livre les premiers contrats API exploitables par le front et les tests.
Assigne a : `Thomas`

3. `FEAT1.3` Initialisation frontend (framework, architecture composants, UI kit).
Mini resume : Fournit le socle d'interface pour brancher rapidement les parcours metier.
Assigne a : `Mohamed`

4. `FEAT1.4` Setup GitFlow + protection branches + premieres CI checks.
Mini resume : Installe les garde-fous qualite pour eviter regressions et merges risques.
Assigne a : `Yohann`

5. `FEAT1.5` Creation des premiers Dockerfile et environnement local conteneurise.
Mini resume : Homogeneise l'execution entre machines dev et prepare le futur deploiement.
Assigne a : `Yohann`

6. `FEAT1.6` Generation d'un mock dataset commandes/profils pour l'equipe data.
Mini resume : Permet de demarrer l'analyse BI/ML sans attendre des volumes reels.
Assigne a : `Daniel`

## Sprint 2 - Logique metier et Cloud v1 (Semaines 4 a 6)

### User Stories (Users)

1. `US2.1` En tant que client, je peux ajouter des produits au panier et passer une commande.
Mini resume : Implante le tunnel d'achat principal de la marketplace.

2. `US2.2` En tant que client, je peux payer ma commande via un paiement simule.
Mini resume : Finalise l'acte d'achat et ferme le cycle commande -> paiement.

3. `US2.3` En tant que client, je peux consulter l'historique et le detail de mes commandes.
Mini resume : Renforce la transparence post-achat et la confiance utilisateur.

4. `US2.4` En tant que producteur, je peux mettre a jour mes stocks et le statut d'expedition.
Mini resume : Garantit le suivi operationnel cote vendeur.

5. `US2.5` En tant qu'equipe data, je peux explorer les premieres donnees pour produire des insights initiaux.
Mini resume : Lance les analyses metier des que les flux transactionnels existent.

### Features techniques

1. `FEAT2.1` Endpoints commandes (`POST/GET /orders`) et gestion cycle de vie commande.
Mini resume : Structure les etats metier de la commande et leur persistance.
Assigne a : `Thomas`

2. `FEAT2.2` Endpoint paiement simule (`POST /payments`) avec cas d'erreur controles.
Mini resume : Cree un comportement realiste pour tester robustesse metier et SRE.
Assigne a : `Thomas`

3. `FEAT2.3` Connexion front-back du parcours catalogue/panier/checkout.
Mini resume : Transforme les APIs en experience utilisateur complete et testable.
Assigne a : `Mohamed`

4. `FEAT2.4` Conteneurisation complete via docker-compose + images front/back.
Mini resume : Standardise l'environnement d'execution pre-prod.
Assigne a : `Yohann`

5. `FEAT2.5` Pipeline CI/CD vers environnement cloud (staging/dev cluster).
Mini resume : Automatise build, push et deploiement pour livrer une v1 frequente.
Assigne a : `Yohann`

6. `FEAT2.6` Scripts de clustering initiaux + prototype Power BI connecte.
Mini resume : Produit les premiers segments clients/producteurs et visualisations.
Assigne a : `Daniel`

7. `FEAT2.7` Prototype dashboard BI sur Power BI a partir des donnees de test.
Mini resume : Couvre explicitement le livrable analytique attendu par le sujet.
Assigne a : `Manon`

## Sprint 3 - Fiabilite SRE et pipeline Data final (Semaines 7 a 9)

### User Stories (Users)

1. `US3.1` En tant qu'utilisateur, je beneficie d'une application plus stable et reactive.
Mini resume : Cible la reduction des erreurs 5xx et des latences sur les endpoints critiques.

2. `US3.2` En tant qu'utilisateur, je vois des messages d'erreur clairs en cas de timeout ou panne.
Mini resume : Ameliore l'UX dans les situations degradees et reduit la frustration.

3. `US3.3` En tant que PO, je peux suivre des indicateurs SLO/SLI sur des dashboards de monitoring.
Mini resume : Permet le pilotage produit par la fiabilite, pas seulement par les features.

4. `US3.4` En tant qu'analyste metier, je peux consulter anomalies et segments clients finalises.
Mini resume : Rend les analyses actionnables pour decision business.

### Features techniques

1. `FEAT3.1` Instrumentation backend (latence, erreurs, taux succes) exportable Prometheus.
Mini resume : Rend mesurable la qualite de service en temps reel.
Assigne a : `Thomas`

2. `FEAT3.2` Stack observabilite Prometheus + Grafana avec dashboards SRE.
Mini resume : Centralise la supervision technique et la consommation d'error budget.
Assigne a : `Yohann`

3. `FEAT3.3` Definition et suivi des SLI/SLO/SLA dans l'exploitation.
Mini resume : Formalise des objectifs de fiabilite exploitables en decision de release.
Assigne a : `Yohann`

4. `FEAT3.4` Durcissement frontend sur gestion erreurs HTTP 500 et timeouts.
Mini resume : Evite les blocages UI et preserve une experience utilisateur continue.
Assigne a : `Mohamed`

5. `FEAT3.5` Pipeline data final : detection anomalies + injection resultats en base.
Mini resume : Industrialise la chaine data pour analyses repetables.
Assigne a : `Daniel`

6. `FEAT3.6` Exposition des endpoints analytiques (`/data/sales-metrics`, `/data/clustering/customers`, `/data/anomalies`).
Mini resume : Ouvre la consommation des insights par BI et eventuellement le front.
Assigne a : `Thomas`

7. `FEAT3.7` Mise a disposition des donnees via SQL read-only et API pour l'equipe data.
Mini resume : Satisfait l'exigence sujet de fournir un acces SQL ou API aux donnees.
Assigne a : `Yohann`

8. `FEAT3.8` Formalisation de 3 analyses minimales (comportement, anomalies, segmentation).
Mini resume : Verifie explicitement la conformite avec les analyses imposees.
Assigne a : `Daniel`

## Sprint 4 - Stabilisation finale, charge et soutenance (Semaines 10 a 12)

### User Stories (Users)

1. `US4.1` En tant qu'utilisateur, je peux utiliser la plateforme sans blocages critiques.
Mini resume : Priorise correction des bugs majeurs plutot que nouvelles fonctions.

2. `US4.2` En tant que product owner, je peux valider que les engagements SLA sont tenus.
Mini resume : Confirme que la plateforme est defensible en soutenance et en exploitation.

3. `US4.3` En tant qu'enseignant/client fictif, je peux voir une demo complete et coherente.
Mini resume : Assure une presentation claire des composants produit, DevOps, SRE et Data.

### Features techniques

1. `FEAT4.1` Campagne de bugfix critique front/back et reduction dette restante.
Mini resume : Stabilise la release finale et limite les regressions visibles.
Assigne a : `Mohamed`

2. `FEAT4.2` Tests de charge (k6/JMeter) et verification des alertes SRE.
Mini resume : Valide la tenue sous charge et l'efficacite du monitoring.
Assigne a : `Yohann`

3. `FEAT4.3` Ajustement du scaling Kubernetes selon resultats de charge.
Mini resume : Optimise performance/cout tout en restant dans les objectifs de fiabilite.
Assigne a : `Yohann`

4. `FEAT4.4` Finalisation dashboard analytique et controle integrite des donnees.
Mini resume : Verifie la coherence des insights, y compris apres tests de charge.
Assigne a : `Manon`

5. `FEAT4.5` Packaging des livrables (docs architecture, workflow, repetition soutenance).
Mini resume : Rend le projet presentable et evaluable sans zones floues.
Assigne a : `Thomas`

6. `FEAT4.6` Finalisation du diagramme d'architecture pour la soutenance.
Mini resume : Couvre explicitement le livrable "Architecture diagramme" du sujet.
Assigne a : `Thomas`

## Cartes Scrum recurrentes (a dupliquer a chaque sprint)

1. `SCRUM.1` Sprint Planning (debut de sprint).
Mini resume : Selection des US/FEAT du sprint et estimation de charge.
Assigne a : `Yohann`

2. `SCRUM.2` Daily Scrum (quotidien ou 3x/semaine).
Mini resume : Synchronisation rapide, suivi avancement, blocages et plan du jour.
Assigne a : `Yohann`

3. `SCRUM.3` Dev Sync et Code Review (continu).
Mini resume : Garantit PR relues et conformes au workflow qualite.
Assigne a : `Thomas`

4. `SCRUM.4` Sprint Review (fin de sprint).
Mini resume : Demo increment et validation PO avant cloture de sprint.
Assigne a : `Thomas`

5. `SCRUM.5` Retrospective (apres review).
Mini resume : Capitalise les ameliorations de process pour le sprint suivant.
Assigne a : `Yohann`

## Suggestion de colonnes Kanban

- `Backlog`
- `Sprint backlog`
- `In progress`
- `Review/Test`
- `Done`

## Etiquettes conseillees

- `US` (jaune)
- `FEAT` (bleu)
- `SRE` (rouge)
- `DATA` (vert)
- `DEVOPS` (orange)
- `FRONT` (violet)
- `BACK` (gris)
