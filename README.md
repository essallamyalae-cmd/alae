# Application PFE — Gestion des absences et des notes

## 1) Objectif
Application web responsive pour un établissement universitaire permettant :
- la gestion pédagogique (filières, années, semestres, groupes, modules)
- la saisie des absences par séance
- la saisie des notes de contrôle et d'examen
- la génération automatique d'avertissements
- la détection des étudiants abandonnés
- l'affichage de statistiques et dashboards décisionnels

## 2) Stack technique
- **Frontend** : HTML, CSS, Bootstrap 5, JavaScript, Chart.js
- **Backend** : Python Flask + SQLAlchemy
- **Base de données** : MySQL

## 3) Arborescence du projet
```text
pfe_absences_notes/
├── app.py
├── requirements.txt
├── schema.sql
├── README.md
├── docs/
│   ├── MCD_MLD.md
│   └── architecture.md
├── static/
│   ├── css/style.css
│   └── js/app.js
└── templates/
    ├── base.html
    ├── login.html
    ├── admin_dashboard.html
    ├── students.html
    ├── modules.html
    ├── groups.html
    ├── prof_dashboard.html
    ├── absence_entry.html
    ├── note_entry.html
    ├── student_history.html
    ├── statistics.html
    └── abandoned_students.html
```

## 4) Installation
### Créer l'environnement
```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Configurer MySQL
Créer la base :
```sql
SOURCE schema.sql;
```

### Définir la variable de connexion
Exemple Windows PowerShell :
```powershell
$env:DATABASE_URL="mysql+pymysql://root:motdepasse@localhost/pfe_absences_notes"
python app.py
```

Exemple Linux / Mac :
```bash
export DATABASE_URL="mysql+pymysql://root:motdepasse@localhost/pfe_absences_notes"
python app.py
```

## 5) Initialiser les données de démonstration
Lancer l'application puis ouvrir :
```text
http://127.0.0.1:5000/seed
```

Comptes démo :
- Admin : `admin / admin123`
- Professeur : `sara.prof / prof123`

## 6) Fonctionnalités disponibles
### Administration
- Dashboard global
- Gestion des étudiants
- Gestion des groupes
- Gestion des modules
- Liste des étudiants abandonnés
- Statistiques décisionnelles

### Professeur
- Dashboard personnel
- Saisie des absences par séance
- Saisie des notes
- Consultation de l'historique étudiant

## 7) Règles de gestion implémentées
- 1 absence → premier avertissement
- 2 absences → deuxième avertissement
- 3 absences ou plus → conseil de discipline
- Étudiant absent à un examen **et** sans aucune note → statut `abandonné`
- Les étudiants abandonnés sont exclus des statistiques principales

## 8) Limites actuelles à améliorer pour la soutenance
Cette version est **fonctionnelle pour une démonstration PFE**, mais tu peux encore ajouter :
- upload réel des photos
- CRUD complet avec modification/suppression
- export PDF / Excel
- API REST séparée
- authentification plus sécurisée (Flask-Login, rôles détaillés)
- data warehouse + Power BI / Metabase pour la vraie partie BI avancée
