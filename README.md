---
title: UMbb Exam Manager
emoji: 🏢
colorFrom: blue
colorTo: dark-indigo
sdk: streamlit
app_file: frontend/app.py
pinned: false
---

# Gestionnaire d'Examens - Université de Boumerdès

Ce projet est une application Streamlit permettant la gestion et la validation des plannings d'examens.

## Déploiement Cloud
- **BDD** : Neon Postgres (Serverless)
- **Interface** : Hugging Face Spaces

## Configuration Locale
1. Installer les dépendances : `pip install -r requirements.txt`
2. Configurer le `.env` avec votre `DATABASE_URL`.
3. Lancer l'app : `streamlit run frontend/app.py`
