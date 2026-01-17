-- =====================================================
-- SCHÉMA DE LA BASE DE DONNÉES - projet_bda
-- =====================================================


-- Table: departements
CREATE TABLE departements (id integer NOT NULL, nom character varying(150) NOT NULL);

-- Table: etudiants
CREATE TABLE etudiants (id integer NOT NULL, nom character varying(100), prenom character varying(100), formation_id integer, annee_univ character varying(9));

-- Table: examens
CREATE TABLE examens (id integer NOT NULL, module_id integer, salle_id integer, prof_id integer, date_heure timestamp without time zone, duree integer);

-- Table: formations
CREATE TABLE formations (id integer NOT NULL, nom character varying(200) NOT NULL, niveau character varying(2), dept_id integer);

-- Table: inscriptions
CREATE TABLE inscriptions (id integer NOT NULL, etudiant_id integer NOT NULL, module_id integer NOT NULL);

-- Table: modules
CREATE TABLE modules (id integer NOT NULL, nom character varying(200) NOT NULL, credits integer, formation_id integer);

-- Table: parametres
CREATE TABLE parametres (cle character varying(50) NOT NULL, valeur character varying(100));

-- Table: professeurs
CREATE TABLE professeurs (id integer NOT NULL, nom character varying(150), dept_id integer, specialite character varying(150));

-- Table: salles
CREATE TABLE salles (id integer NOT NULL, nom character varying(50), capacite integer, type character varying(20), bloc character varying(20));

-- Table: users
CREATE TABLE users (id integer NOT NULL, username character varying(100) NOT NULL, password_hash character varying(256) NOT NULL, role character varying(20) NOT NULL, ref_id integer, email character varying(150) NOT NULL);

-- Table: validation_pedagogique
CREATE TABLE validation_pedagogique (id integer NOT NULL, formation_id integer, statut character varying(20), commentaire text, date_maj timestamp without time zone);


-- =====================================================
-- CONTRAINTES
-- =====================================================

-- departements: departements_pkey
ALTER TABLE departements ADD CONSTRAINT departements_pkey PRIMARY KEY (id);

-- departements: departements_nom_key
ALTER TABLE departements ADD CONSTRAINT departements_nom_key UNIQUE (nom);

-- etudiants: etudiants_formation_id_fkey
ALTER TABLE etudiants ADD CONSTRAINT etudiants_formation_id_fkey FOREIGN KEY (formation_id) REFERENCES formations(id);

-- etudiants: etudiants_pkey
ALTER TABLE etudiants ADD CONSTRAINT etudiants_pkey PRIMARY KEY (id);

-- examens: examens_module_id_fkey
ALTER TABLE examens ADD CONSTRAINT examens_module_id_fkey FOREIGN KEY (module_id) REFERENCES modules(id);

-- examens: examens_salle_id_fkey
ALTER TABLE examens ADD CONSTRAINT examens_salle_id_fkey FOREIGN KEY (salle_id) REFERENCES salles(id);

-- examens: examens_prof_id_fkey
ALTER TABLE examens ADD CONSTRAINT examens_prof_id_fkey FOREIGN KEY (prof_id) REFERENCES professeurs(id);

-- examens: examens_pkey
ALTER TABLE examens ADD CONSTRAINT examens_pkey PRIMARY KEY (id);

-- formations: formations_niveau_check
ALTER TABLE formations ADD CONSTRAINT formations_niveau_check CHECK (((niveau)::text = ANY ((ARRAY['L1'::character varying, 'L2'::character varying, 'L3'::character varying, 'M1'::character varying, 'M2'::character varying])::text[])));

-- formations: formations_dept_id_fkey
ALTER TABLE formations ADD CONSTRAINT formations_dept_id_fkey FOREIGN KEY (dept_id) REFERENCES departements(id) ON DELETE CASCADE;

-- formations: formations_pkey
ALTER TABLE formations ADD CONSTRAINT formations_pkey PRIMARY KEY (id);

-- inscriptions: fk_etudiant
ALTER TABLE inscriptions ADD CONSTRAINT fk_etudiant FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE;

-- inscriptions: fk_module
ALTER TABLE inscriptions ADD CONSTRAINT fk_module FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE;

-- inscriptions: inscriptions_pkey
ALTER TABLE inscriptions ADD CONSTRAINT inscriptions_pkey PRIMARY KEY (id);

-- inscriptions: unique_inscription
ALTER TABLE inscriptions ADD CONSTRAINT unique_inscription UNIQUE (etudiant_id, module_id);

-- modules: modules_formation_id_fkey
ALTER TABLE modules ADD CONSTRAINT modules_formation_id_fkey FOREIGN KEY (formation_id) REFERENCES formations(id) ON DELETE CASCADE;

-- modules: modules_pkey
ALTER TABLE modules ADD CONSTRAINT modules_pkey PRIMARY KEY (id);

-- parametres: parametres_pkey
ALTER TABLE parametres ADD CONSTRAINT parametres_pkey PRIMARY KEY (cle);

-- professeurs: professeurs_dept_id_fkey
ALTER TABLE professeurs ADD CONSTRAINT professeurs_dept_id_fkey FOREIGN KEY (dept_id) REFERENCES departements(id);

-- professeurs: professeurs_pkey
ALTER TABLE professeurs ADD CONSTRAINT professeurs_pkey PRIMARY KEY (id);

-- salles: salles_pkey
ALTER TABLE salles ADD CONSTRAINT salles_pkey PRIMARY KEY (id);

-- users: users_pkey
ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id);

-- users: users_email_unique
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);

-- users: users_username_key
ALTER TABLE users ADD CONSTRAINT users_username_key UNIQUE (username);

-- validation_pedagogique: validation_pedagogique_formation_id_fkey
ALTER TABLE validation_pedagogique ADD CONSTRAINT validation_pedagogique_formation_id_fkey FOREIGN KEY (formation_id) REFERENCES formations(id);

-- validation_pedagogique: validation_pedagogique_pkey
ALTER TABLE validation_pedagogique ADD CONSTRAINT validation_pedagogique_pkey PRIMARY KEY (id);

-- validation_pedagogique: unique_formation
ALTER TABLE validation_pedagogique ADD CONSTRAINT unique_formation UNIQUE (formation_id);

