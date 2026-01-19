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
    Priorité à l'URL définie dans les variables d'environnement.
    """
    db_url = os.getenv("DATABASE_URL")
    
    try:
        if db_url:
            # Connexion au Cloud (Neon)
            return psycopg2.connect(db_url)
        else:
            # Connexion Locale
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
    except psycopg2.Error as e:
        print(f"❌ Erreur de connexion BDD : {e}")
        return None

if __name__ == "__main__":
    # Test unitaire pour vérifier la connexion sans lancer Streamlit
    conn = get_connection()
    if conn:
        print("✅ Connexion réussie au module Database.")
        conn.close()
    else:
        print("❌ Échec de la connexion. Vérifiez vos identifiants dans DB_CONFIG.")