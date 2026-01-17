# Système de Gestion Automatisée des Examens (BDA Project)

Ce projet est une solution complète de gestion et de planification d'examens universitaires, combinant une base de données PostgreSQL optimisée et une interface web interactive Streamlit. Il répond aux problématiques de conflits d'horaires et de gestion des ressources (salles, surveillants).

## 🚀 Fonctionnalités Clés

- **Planification Automatique** : Algorithme heuristique pour générer des emplois du temps sans conflits.
- **Gestion Multi-Rôles** :
  - **Admin** : Génération globale, paramètres, gestion utilisateurs.
  - **Doyen** : Tableaux de bord stratégiques (KPIs, stats).
  - **Chef de Département** : Validation pédagogique des plannings.
  - **Professeurs** : Consultation de planning et surveillances.
  - **Étudiants** : Consultation personnalisée.
- **Base de Données Robuste** :
  - Intégrité référentielle stricte.
  - Triggers de validation (Capacité salle, Audit).
  - Optimisation par index.
- **Rapports** : Génération PDF, KPIs temps réel.

## 🛠️ Installation

### Prérequis
- Python 3.8+
- PostgreSQL 13+

### 1. Configuration de la Base de Données
1. Créez une base de données PostgreSQL nommée `projet_bda`.
2. Exécutez les scripts SQL dans l'ordre :
   ```bash
   psql -U postgres -d projet_bda -f database/shema.sql
   psql -U postgres -d projet_bda -f database/data.sql
   psql -U postgres -d projet_bda -f database/functions.sql
   ```
   *(Ou utilisez le script Python `apply_db_updates.py` si les données existent déjà)*

### 2. Installation du Backend
```bash
pip install -r requirements.txt
```

### 3. Lancement de l'Application
```bash
streamlit run frontend/app.py
```

## 🔐 Comptes de Démonstration (Réinitialisables via `reset_auth.py`)

| Rôle | Email | Mot de Passe |
|------|-------|--------------|
| **Admin** | `admin@umbb.dz` | `admin123` |
| **Doyen** | `doyen@umbb.dz` | `123456` |
| **Professeur** | (Généré en DB) | `prof123` |
| **Étudiant** | (Généré en DB) | `etud123` |

## 📂 Structure du Projet

```
Projet_BDA/
├── backend/            # Logique métier et accès données
│   ├── db.py          # Connexion (Singleton)
│   ├── auth.py        # Authentification
│   ├── admin.py       # Logique Admin & Algorithme
│   ├── chef.py        # Logique Chef Dept
│   └── ...
├── database/           # Scripts SQL
│   ├── shema.sql      # Création tables
│   ├── data.sql       # Données de test
│   └── functions.sql  # Triggers & Procédures
├── frontend/           # Interface Streamlit
│   └── app.py         # Point d'entrée unique
├── benchmark_performance.py # Tests de charge
├── generate_rapport.py      # Générateur de PDF technique
└── requirements.txt
```

## 📊 Benchmarks et Performance
Le système est optimisé pour gérer :
- 13 000+ Étudiants
- 130 000+ Inscriptions
- Indexation sur `date_heure` et `module_id` pour des requêtes < 0.1s.

Commande pour lancer les tests :
```bash
python benchmark_performance.py
```

## 📝 Auteurs
- **[Votre Nom]**
- **[Nom Binôme 1]**
- **[Nom Binôme 2]**
