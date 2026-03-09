# Retrospective Sprint 1

## Contexte

Le sprint 1 avait pour objectif de poser les fondations de la Marketplace Locale Intelligente: structure du backend, schéma de base de données, premiers endpoints métier, base frontend, règles de collaboration Git et premiers éléments DevOps. Le dépôt montre qu'à la fin du sprint, l'équipe a effectivement livré un socle transverse exploitable par les profils backend, frontend, DevOps et data.

Cette rétrospective synthétise le déroulement du sprint, les points saillants, les difficultés rencontrées et les décisions d'amélioration à appliquer dès le sprint 2.

## Bilan global du sprint

Le sprint est globalement positif. L'équipe a réussi à produire un incrément réel, visible et cohérent au lieu d'accumuler uniquement de la préparation théorique. La structure technique du projet est désormais installée: API FastAPI versionnée, schéma PostgreSQL, frontend React/Vite, conteneurisation initiale, pipeline CI backend et dataset mock pour l'équipe data.

Le point important est que les livrables ne sont pas isolés. Ils forment déjà une chaîne de valeur partielle:

- le backend expose les premiers contrats API utiles au frontend;
- le frontend consomme déjà les endpoints d'authentification et de catalogue;
- la base de données a été pensée pour le transactionnel et l'analytique;
- Docker et la CI commencent à sécuriser l'industrialisation;
- l'équipe data peut démarrer sans attendre les vraies données de production.

En revanche, le sprint montre aussi une tension classique de début de projet: beaucoup de périmètres ont été ouverts en parallèle, avec une profondeur de finition encore inégale selon les briques.

## Ce qui a bien fonctionné

### 1. Une vraie base produit a été livrée

Le sprint ne s'est pas limité à une simple initialisation de repository. Les éléments visibles et structurants sont bien présents:

- inscription et authentification;
- récupération du profil utilisateur;
- listing des produits;
- listing des producteurs;
- socle UI frontend immédiatement réutilisable;
- environnement conteneurisé de base.

Cela donne une matière concrète pour une review de sprint crédible.

### 2. L'architecture a été pensée assez tôt

Le projet a pris de bonnes décisions de structure dès le départ:

- séparation claire frontend / backend / data / docs;
- versionnement des endpoints sous `/api/v1`;
- schéma SQL préparé pour les besoins analytiques futurs;
- documentation d'architecture et de workflow déjà rédigée.

Cette anticipation réduit le risque de refonte brutale en sprint 2 ou 3.

### 3. La dimension data n'a pas été oubliée

Le script de seed, le notebook d'exploration et la conception du schéma montrent un bon réflexe produit: les besoins data ont été pris en compte dès le début, au lieu d'être traités comme un sujet secondaire en fin de projet.

### 4. La collaboration par PR semble avoir été respectée

L'historique Git montre une progression par branches et merges successifs sur des thèmes cohérents: fondations backend, mock data, auth et CRUD, DevOps, puis frontend. C'est un bon signal de discipline collective pour un sprint 1.

## Ce qui a moins bien fonctionné

### 1. Le niveau de finition n'est pas homogène

Certaines briques sont solides et bien posées, mais d'autres restent au stade de base fonctionnelle. Le cas le plus visible est la user story catalogue:

- la liste des produits existe;
- l'endpoint de détail produit existe côté API;
- mais le parcours de détail produit n'est pas encore matérialisé de bout en bout côté frontend.

Résultat: une story peut sembler terminée vue depuis l'architecture, alors qu'elle ne l'est pas encore complètement du point de vue utilisateur.

### 2. La qualité automatisée reste trop légère

Le dépôt contient une première CI, ce qui est une bonne chose, mais la couverture reste limitée:

- les checks versionnés portent surtout sur le backend;
- les tests sont peu nombreux;
- le frontend n'est pas encore inclus de façon équivalente dans la chaîne de validation;
- la reproductibilité locale dépend encore d'une installation manuelle des dépendances.

Pour un sprint de fondation, c'est compréhensible. Pour la suite, ce ne sera plus suffisant.

### 3. L'intégration front-back n'est pas complètement stabilisée

Le frontend montre déjà une ambition supérieure au périmètre du sprint 1, avec des pages et routes préparées pour le panier et les commandes. C'est utile pour prendre de l'avance, mais cela crée aussi des incohérences temporaires:

- certaines routes ou redirections semblent préparées avant que tous les écrans correspondants soient finalisés;
- la définition de “Done” n'a probablement pas été assez stricte sur certains parcours.

Le risque est de présenter un produit qui paraît plus avancé qu'il ne l'est réellement sur les flux complets.

### 4. Le front a visiblement avancé rapidement en fin de sprint

L'historique Git suggère une intégration frontend importante en fin de sprint. Ce n'est pas anormal, mais cela concentre le risque:

- moins de temps pour stabiliser les interactions avec le backend;
- moins de temps pour corriger les écarts avant la review;
- plus forte probabilité de détails d'intégration restants.

## Difficultés rencontrées

### Difficulté technique

Le projet combine dès le départ plusieurs chantiers exigeants:

- modélisation de la donnée transactionnelle;
- sécurité minimale via authentification JWT;
- mise en place de l'API;
- initialisation d'un frontend moderne;
- conteneurisation;
- préparation d'un futur usage data.

Sur un sprint 1, la difficulté principale n'est pas la complexité d'une feature isolée, mais la coordination de plusieurs fondations interdépendantes.

### Difficulté d'alignement sur le périmètre réel

Comme souvent sur un sprint de lancement, l'équipe a dû arbitrer entre:

- finir complètement peu de parcours;
- ou poser un maximum de briques pour sécuriser la suite.

Le dépôt montre qu'un choix intermédiaire a été fait: plusieurs briques ont été ouvertes rapidement, avec un niveau de finition variable. C'était probablement le bon arbitrage pour protéger le planning global, mais cela doit maintenant être compensé par un resserrement du “Done”.

### Difficulté d'industrialisation complète dès le départ

Les premiers éléments DevOps sont là, mais industrialiser complètement backend, frontend, tests et validation locale dès le sprint 1 reste coûteux. L'équipe a priorisé un pipeline initial utile plutôt qu'une usine complète. Le compromis est acceptable, à condition de renforcer cela immédiatement au sprint 2.

## Analyse des causes

### Cause 1. Le sprint 1 portait trop d'objectifs transverses

Le sprint devait à la fois lancer le produit, l'infra, la donnée et le mode de travail collectif. C'est normal sur un projet académique de ce type, mais cela crée mécaniquement une dispersion de l'effort.

### Cause 2. Les critères d'acceptation n'étaient pas toujours assez orientés parcours utilisateur complet

Quand un endpoint existe, un développeur peut considérer qu'une story est presque finie. Quand une page existe, un autre peut considérer la même chose. Or, pour le Product Owner, une story n'est réellement terminée que lorsque le flux est cohérent de bout en bout.

### Cause 3. Le contrôle qualité n'est pas encore assez intégré au rythme de livraison

La CI existe, mais elle ne couvre pas encore suffisamment les zones où les écarts d'intégration apparaissent. Cela laisse passer des zones grises entre “présent dans le code” et “prêt à être démontré sereinement”.

## Stop / Keep / Start

### Stop

- arrêter de considérer une story comme terminée dès qu'une moitié du flux est prête;
- arrêter d'ouvrir trop de routes ou écrans avant d'avoir sécurisé les parcours critiques du sprint;
- arrêter de repousser la consolidation de l'intégration front-back à la toute fin du sprint.

### Keep

- conserver la logique de travail par branches et Pull Requests;
- conserver la bonne anticipation architecture / data / DevOps;
- conserver le découpage clair du dépôt et la documentation structurée;
- conserver la dynamique de livraison concrète à chaque sprint.

### Start

- définir une vraie checklist de “Definition of Done” commune à toute l'équipe;
- inclure le frontend dans les validations automatisées au même niveau que le backend;
- ajouter des scénarios de tests simples mais représentatifs sur les flux critiques;
- verrouiller en début de sprint la liste des parcours démontrables en review;
- traiter immédiatement les petites incohérences de routing ou d'intégration avant d'ouvrir de nouvelles surfaces.

## Actions d'amélioration décidées pour le sprint 2

### Action 1. Formaliser une Definition of Done commune

Une story ne sera considérée comme terminée que si les conditions suivantes sont réunies:

- code intégré sur la branche cible;
- parcours fonctionnel testable de bout en bout sur le périmètre annoncé;
- absence d'incohérence de routing ou d'écran manquant sur le flux concerné;
- documentation minimale ou consignes d'usage disponibles si nécessaire.

### Action 2. Renforcer la qualité automatisée

Objectif sprint 2:

- ajouter la validation build frontend dans la CI;
- compléter les tests backend sur les endpoints déjà exposés;
- rendre la validation locale plus simple à rejouer pour toute l'équipe.

### Action 3. Réserver un temps explicite de consolidation avant la review

Une fenêtre de stabilisation devra être prévue en fin de sprint pour:

- vérifier les parcours de démo;
- corriger les redirections cassées ou écrans incomplets;
- sécuriser la cohérence entre backlog, démo et code réellement fusionné.

### Action 4. Prioriser les flux complets avant les ouvertures de périmètre

Le sprint 2 devra d'abord garantir un tunnel cohérent catalogue -> panier -> commande avant d'étendre trop largement la surface fonctionnelle.

## Remarques finales du PO / Lead Dev

Ce sprint 1 remplit son rôle principal: il a transformé une idée de projet en plateforme technique crédible. Le niveau de maturité est satisfaisant pour un démarrage, surtout compte tenu du nombre de dimensions à ouvrir simultanément.

La principale leçon n'est pas qu'il manque des briques majeures. La principale leçon est qu'il faut maintenant augmenter le niveau d'exigence sur la finition, la démontrabilité et la validation automatisée. Autrement dit, le sprint 1 a correctement construit la base; le sprint 2 devra transformer cette base en flux métier vraiment consolidés.

## Conclusion

Le sprint 1 peut être considéré comme réussi, avec une réussite forte sur la mise en place du socle technique et une réussite partielle sur la fermeture complète de certains parcours utilisateurs. L'équipe sort du sprint avec une bonne base, mais aussi avec des enseignements très clairs:

- mieux définir ce qui est vraiment “Done”;
- mieux stabiliser l'intégration front-back;
- mieux étendre l'automatisation qualité;
- mieux préparer la review à partir de scénarios entièrement démontrables.

Si ces points sont traités dès le sprint 2, le projet sera sur une trajectoire nettement plus robuste pour les sprints métier, SRE et data à venir.