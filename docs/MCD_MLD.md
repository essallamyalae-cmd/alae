# MCD et MLD

## MCD (vue conceptuelle)
```mermaid
erDiagram
    FILIERE ||--o{ GROUPE : contient
    ANNEE ||--o{ SEMESTRE : contient
    ANNEE ||--o{ GROUPE : organise
    FILIERE ||--o{ MODULE : propose
    SEMESTRE ||--o{ MODULE : contient
    GROUPE ||--o{ ETUDIANT : contient
    PROFESSEUR ||--o{ MODULE : assure_cours
    MODULE }o--o{ PROFESSEUR : assure_tp
    MODULE ||--o{ SEANCE : planifie
    GROUPE ||--o{ SEANCE : concerne
    ETUDIANT ||--o{ ABSENCE : a
    SEANCE ||--o{ ABSENCE : enregistre
    ETUDIANT ||--o{ NOTE : obtient
    MODULE ||--o{ NOTE : concerne
    SEMESTRE ||--o{ NOTE : porte_sur
    ETUDIANT ||--o{ AVERTISSEMENT : recoit
    PROFESSEUR ||--o| USER : dispose_de

    FILIERE {
      int id
      string nom
      string description
    }
    ANNEE {
      int id
      string libelle
    }
    SEMESTRE {
      int id
      string libelle
      date date_debut
      date date_fin
    }
    GROUPE {
      int id
      string nom
    }
    PROFESSEUR {
      int id
      string nom
      string prenom
      string email
    }
    ETUDIANT {
      int id
      string code_apogee
      string nom
      string prenom
      string email_academique
      string photo
      string statut
    }
    MODULE {
      int id
      string code
      string nom
      int heures_cours
      int heures_tp
      int semaine_debut_cours
      int semaine_fin_cours
      int semaine_debut_tp
      int semaine_fin_tp
    }
    SEANCE {
      int id
      string type_seance
      string jour
      int creneau
      int semaine
      date date_seance
      int duree_heures
    }
    ABSENCE {
      int id
      bool justifiee
      datetime created_at
    }
    NOTE {
      int id
      string type_note
      float valeur
      datetime created_at
    }
    AVERTISSEMENT {
      int id
      string niveau
      string motif
      datetime created_at
    }
    USER {
      int id
      string username
      string password_hash
      string role
    }
```

## MLD (vue logique)
- **FILIERE**(`id`, nom, description)
- **ANNEE**(`id`, libelle)
- **SEMESTRE**(`id`, libelle, date_debut, date_fin, `annee_id`)
- **GROUPE**(`id`, nom, `filiere_id`, `annee_id`)
- **PROFESSEUR**(`id`, nom, prenom, email, specialite)
- **USER**(`id`, username, password_hash, role, `professeur_id`)
- **ETUDIANT**(`id`, code_apogee, nom, prenom, email_academique, photo, statut, `groupe_id`)
- **MODULE**(`id`, code, nom, heures_cours, heures_tp, semaine_debut_cours, semaine_fin_cours, semaine_debut_tp, semaine_fin_tp, `semestre_id`, `filiere_id`, `professeur_cours_id`)
- **MODULE_PROFESSEUR_TP**(`module_id`, `professeur_id`)
- **SEANCE**(`id`, type_seance, jour, creneau, semaine, date_seance, duree_heures, `module_id`, `groupe_id`)
- **ABSENCE**(`id`, `etudiant_id`, `seance_id`, justifiee, created_at)
- **NOTE**(`id`, `etudiant_id`, `module_id`, `semestre_id`, type_note, valeur, created_at)
- **AVERTISSEMENT**(`id`, `etudiant_id`, niveau, motif, created_at)

## Justification métier
- Un module appartient à un semestre et à une filière.
- Un groupe appartient à une filière et une année.
- Un étudiant appartient à un seul groupe.
- Une séance correspond à un module + groupe + jour + créneau + semaine.
- Une absence est enregistrée par étudiant et par séance.
- Les notes sont stockées par étudiant, module et semestre.
- Les avertissements sont générés automatiquement selon le nombre d'absences.
