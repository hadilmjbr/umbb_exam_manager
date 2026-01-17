import psycopg2
import sys

# Configuration de la base de données
# À modifier selon votre configuration locale PostgreSQL
DB_CONFIG = {
    "host": "localhost",
    "database": "projet_bda",
    "user": "postgres",
    "password": "projet_bda",  # ⚠️ Vérifiez bien ce mot de passe !
    "port": 5432
}

def get_connection():
    """
    Établit une connexion sécurisée à la base de données PostgreSQL.
    Retourne l'objet connection ou None en cas d'échec.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
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