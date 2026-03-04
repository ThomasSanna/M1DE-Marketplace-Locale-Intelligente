# Regles GitFlow et Pull Requests (Sprint 1)

Ce document definit la gouvernance minimale du depot pour le Sprint 1.

## Modele de branches
- `main` : branche stable proche production.
- `develop` : branche d'integration pour la prochaine version.
- `feature/<nom>` : branche de travail, creee depuis `develop`.
- `hotfix/<nom>` : correctif urgent, cree depuis `main`.

## Regles Pull Request
- Aucun push direct sur `main` ou `develop`.
- Chaque PR doit avoir au moins 1 approbation.
- La PR doit etre a jour avec la branche cible avant merge.
- Checks obligatoires : `backend-check` et `docker-build-backend` (workflow CI).
- Supprimer la branche source apres merge.

## Parametres recommandes de protection de branches (GitHub)
Appliquer ces regles sur `main` et `develop` :
1. Exiger une Pull Request avant fusion.
2. Exiger au moins 1 approbation.
3. Ignorer les approbations devenues obsoletes apres nouveau commit.
4. Exiger le passage des checks CI avant fusion.
5. Restreindre le push direct (idealement reserve aux admins).

## Strategie de merge
- Preferer `Squash and merge` pour les branches feature.
- Utiliser `Rebase and merge` seulement si cela clarifie l'historique.
- Message de commit recommande : `<scope>: <action courte>`.
