import psycopg2
import sys
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de la base de données locale (Sert de secours si Neon n'est pas configuré)
DB_CONFIG = {
    "host": "localhost",
    "database": "projet_bda",
    "user": "postgres",
    "password": "projet_bda",
    "port": 5432
}

def get_connection():
    """
    Établit une connexion sécurisée à la base de données (Neon ou Local).
    Priorité à l'URL définie dans les secrets Streamlit ou variables d'environnement.
    """
    db_url = None
    
    # 1. Tenter de récupérer via Streamlit Secrets (Cloud)
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            db_url = st.secrets["DATABASE_URL"]
    except:
        pass

    # 2. Tenter de récupérer via Variables d'environnement (Neon Local ou Docker)
    if not db_url:
        db_url = os.getenv("DATABASE_URL")
    
    try:
        if db_url:
            # Nettoyage de l'URL au cas où (guillemets involontaires)
            db_url = db_url.strip("'").strip('"')
            return psycopg2.connect(db_url)
        else:
            # 3. Connexion Locale (Secours)
            return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Erreur critique de connexion BDD : {e}")
        return None

if __name__ == "__main__":
    # Test unitaire pour vérifier la connexion sans lancer Streamlit
    conn = get_connection()
    if conn:
        print("✅ Connexion réussie au module Database.")
        conn.close()
    else:
        print("❌ Échec de la connexion. Vérifiez vos identifiants dans DB_CONFIG.")