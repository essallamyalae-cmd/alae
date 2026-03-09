# Architecture du projet

## Architecture logique
- **Couche présentation** : templates HTML Bootstrap responsive
- **Couche métier** : règles de gestion dans `app.py`
- **Couche données** : MySQL via SQLAlchemy
- **Couche décisionnelle** : agrégations SQL + graphiques Chart.js

## Flux principal
1. Le professeur se connecte.
2. Il voit ses modules.
3. Il choisit un module, un groupe et une séance.
4. Il coche les étudiants absents.
5. Le système enregistre l'absence.
6. Le système calcule automatiquement les avertissements.
7. Le système vérifie la règle d'abandon.
8. Les statistiques admin sont mises à jour.

## Flux notes
1. Le professeur choisit module + groupe.
2. Il saisit les notes de contrôle et d'examen.
3. Les notes sont liées à l'étudiant, au module et au semestre.
4. Les dashboards exploitent ces données.

## Indicateurs décisionnels
- taux d'absence global
- absences par module
- absences par groupe
- moyenne des notes par module
- corrélation absences / notes
- nombre d'étudiants abandonnés
