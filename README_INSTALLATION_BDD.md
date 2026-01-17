# 📋 Guide d'Installation de la Base de Données - Projet BDA

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :
- **PostgreSQL** (version 12 ou supérieure)
- **pgAdmin** (optionnel, pour interface graphique)

### Installation de PostgreSQL

#### Windows
1. Téléchargez PostgreSQL depuis : https://www.postgresql.org/download/windows/
2. Exécutez l'installateur
3. Notez bien le **mot de passe** que vous définissez pour l'utilisateur `postgres`
4. Port par défaut : `5432`

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

---

## 🚀 Restauration de la Base de Données

### Méthode 1 : Ligne de commande (Recommandé)

#### Étape 1 : Décompresser le fichier
Extrayez le fichier `base_donnees_projet_bda.zip` pour obtenir `export_complet.sql`

#### Étape 2 : Créer une nouvelle base de données
```bash
# Se connecter à PostgreSQL
psql -U postgres

# Dans le terminal psql, créer la base
CREATE DATABASE projet_bda;

# Quitter psql
\q
```

#### Étape 3 : Restaurer les données
```bash
# Windows (PowerShell)
psql -U postgres -d projet_bda -f export_complet.sql

# Linux/macOS
psql -U postgres -d projet_bda < export_complet.sql
```

**Note** : Vous devrez entrer le mot de passe PostgreSQL que vous avez défini lors de l'installation.

---

### Méthode 2 : Avec pgAdmin (Interface graphique)

#### Étape 1 : Ouvrir pgAdmin
Lancez pgAdmin et connectez-vous avec vos identifiants PostgreSQL

#### Étape 2 : Créer une nouvelle base
1. Clic droit sur **Databases** → **Create** → **Database**
2. Nom : `projet_bda`
3. Cliquez sur **Save**

#### Étape 3 : Restaurer le fichier SQL
1. Clic droit sur la base `projet_bda` → **Query Tool**
2. Cliquez sur l'icône **Open File** (dossier)
3. Sélectionnez `export_complet.sql`
4. Cliquez sur **Execute** (▶️)

Attendez que l'import se termine (peut prendre quelques secondes).

---

## ✅ Vérification de l'Installation

### Vérifier que les tables sont créées
```sql
-- Se connecter à la base
psql -U postgres -d projet_bda

-- Lister les tables
\dt

-- Vous devriez voir :
-- departements, etudiants, examens, formations, inscriptions,
-- modules, parametres, professeurs, salles, users, validation_pedagogique
```

### Vérifier les données
```sql
-- Compter les étudiants
SELECT COUNT(*) FROM etudiants;
-- Résultat attendu : 661+

-- Voir les départements
SELECT * FROM departements;
```

---

## 🔧 Configuration de l'Application

### Fichier de connexion : `backend/db.py`

Modifiez les paramètres de connexion selon votre configuration :

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "projet_bda",
    "user": "postgres",
    "password": "VOTRE_MOT_DE_PASSE",  # ⚠️ Changez ceci !
    "port": 5432
}
```

### Tester la connexion
```bash
python backend/db.py
```

Si vous voyez `✅ Connexion réussie au module Database.`, tout fonctionne !

---

## 🏃 Lancer l'Application

### Installation des dépendances Python
```bash
pip install -r requirements.txt
```

### Démarrer l'application
```bash
# Depuis le dossier frontend/
streamlit run app.py
```

L'application devrait s'ouvrir dans votre navigateur à l'adresse : `http://localhost:8501`

---

## 🔐 Comptes de Test

Après l'import, vous pouvez vous connecter avec les comptes suivants (si configurés) :

- **Admin** : Vérifiez la table `users` pour les identifiants
- **Doyen** : Vérifiez la table `users` 
- **Chef de département** : Vérifiez la table `users`

```sql
-- Voir tous les utilisateurs
SELECT id, username, role, email FROM users;
```

---

## ❓ Problèmes Courants

### Erreur : "psql: command not found"
**Solution** : Ajoutez PostgreSQL au PATH système
- **Windows** : `C:\Program Files\PostgreSQL\16\bin`
- **Linux/macOS** : Généralement déjà dans le PATH

### Erreur : "FATAL: password authentication failed"
**Solution** : Vérifiez que vous utilisez le bon mot de passe PostgreSQL

### Erreur : "database projet_bda already exists"
**Solution** : 
```sql
DROP DATABASE projet_bda;
CREATE DATABASE projet_bda;
```

### Les tables sont vides après l'import
**Solution** : Vérifiez que vous avez bien importé `export_complet.sql` et non `shema.sql`

---

## 📞 Support

Pour toute question ou problème, contactez l'administrateur du projet.

---

## 📊 Contenu de la Base de Données

- **11 tables** : Structure complète du système de gestion universitaire
- **661+ étudiants** : Données de test complètes
- **Formations** : L1, L2, L3, M1, M2 dans différents départements
- **Modules** : Cours et crédits associés
- **Examens** : Planification des examens avec salles et professeurs
- **Utilisateurs** : Système d'authentification multi-rôles

---

**Date d'export** : 2026-01-17  
**Version PostgreSQL recommandée** : 12+
