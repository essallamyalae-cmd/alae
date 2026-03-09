CREATE DATABASE IF NOT EXISTS pfe_absences_notes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pfe_absences_notes;

CREATE TABLE annee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libelle VARCHAR(50) NOT NULL
);

CREATE TABLE filiere (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    description TEXT
);

CREATE TABLE semestre (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libelle VARCHAR(10) NOT NULL,
    date_debut DATE,
    date_fin DATE,
    annee_id INT NOT NULL,
    CONSTRAINT fk_semestre_annee FOREIGN KEY (annee_id) REFERENCES annee(id)
);

CREATE TABLE groupe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    filiere_id INT NOT NULL,
    annee_id INT NOT NULL,
    CONSTRAINT fk_groupe_filiere FOREIGN KEY (filiere_id) REFERENCES filiere(id),
    CONSTRAINT fk_groupe_annee FOREIGN KEY (annee_id) REFERENCES annee(id)
);

CREATE TABLE professeur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    specialite VARCHAR(120)
);

CREATE TABLE utilisateur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    professeur_id INT NULL,
    CONSTRAINT fk_utilisateur_professeur FOREIGN KEY (professeur_id) REFERENCES professeur(id)
);

CREATE TABLE etudiant (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code_apogee VARCHAR(50) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email_academique VARCHAR(150) NOT NULL UNIQUE,
    photo VARCHAR(255),
    statut VARCHAR(20) DEFAULT 'actif',
    groupe_id INT NOT NULL,
    CONSTRAINT fk_etudiant_groupe FOREIGN KEY (groupe_id) REFERENCES groupe(id)
);

CREATE TABLE module (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    nom VARCHAR(150) NOT NULL,
    semestre_id INT NOT NULL,
    filiere_id INT NOT NULL,
    heures_cours INT DEFAULT 0,
    heures_tp INT DEFAULT 0,
    semaine_debut_cours INT,
    semaine_fin_cours INT,
    semaine_debut_tp INT,
    semaine_fin_tp INT,
    professeur_cours_id INT NULL,
    CONSTRAINT fk_module_semestre FOREIGN KEY (semestre_id) REFERENCES semestre(id),
    CONSTRAINT fk_module_filiere FOREIGN KEY (filiere_id) REFERENCES filiere(id),
    CONSTRAINT fk_module_professeur_cours FOREIGN KEY (professeur_cours_id) REFERENCES professeur(id)
);

CREATE TABLE module_professeur_tp (
    module_id INT NOT NULL,
    professeur_id INT NOT NULL,
    PRIMARY KEY (module_id, professeur_id),
    CONSTRAINT fk_mpt_module FOREIGN KEY (module_id) REFERENCES module(id),
    CONSTRAINT fk_mpt_prof FOREIGN KEY (professeur_id) REFERENCES professeur(id)
);

CREATE TABLE seance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    groupe_id INT NOT NULL,
    type_seance VARCHAR(20) NOT NULL,
    jour VARCHAR(20) NOT NULL,
    creneau INT NOT NULL,
    semaine INT NOT NULL,
    date_seance DATE NOT NULL,
    duree_heures INT DEFAULT 4,
    CONSTRAINT fk_seance_module FOREIGN KEY (module_id) REFERENCES module(id),
    CONSTRAINT fk_seance_groupe FOREIGN KEY (groupe_id) REFERENCES groupe(id)
);

CREATE TABLE absence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    seance_id INT NOT NULL,
    justifiee BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_absence_etudiant_seance (etudiant_id, seance_id),
    CONSTRAINT fk_absence_etudiant FOREIGN KEY (etudiant_id) REFERENCES etudiant(id),
    CONSTRAINT fk_absence_seance FOREIGN KEY (seance_id) REFERENCES seance(id)
);

CREATE TABLE note (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    module_id INT NOT NULL,
    semestre_id INT NOT NULL,
    type_note VARCHAR(20) NOT NULL,
    valeur DECIMAL(5,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_note_etudiant FOREIGN KEY (etudiant_id) REFERENCES etudiant(id),
    CONSTRAINT fk_note_module FOREIGN KEY (module_id) REFERENCES module(id),
    CONSTRAINT fk_note_semestre FOREIGN KEY (semestre_id) REFERENCES semestre(id)
);

CREATE TABLE avertissement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    niveau VARCHAR(50) NOT NULL,
    motif VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_avertissement_etudiant FOREIGN KEY (etudiant_id) REFERENCES etudiant(id)
);
