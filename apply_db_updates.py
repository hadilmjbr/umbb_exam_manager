import os
import sys
from backend.db import get_connection

def apply_updates():
    print("🔄 Application des mises à jour de la base de données (Triggers, Fonctions, Index)...")
    
    file_path = os.path.join("database", "functions.sql")
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        return

    try:
        conn = get_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base de données.")
            return

        cur = conn.cursor()
        
        with open(file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
            
        # Execute the script
        cur.execute(sql_content)
        conn.commit()
        
        print("✅ Mises à jour appliquées avec succès !")
        print("   - Fonctions stockées créées")
        print("   - Trigger de capacité salle activé")
        print("   - Trigger d'audit activé")
        print("   - Index de performance créés")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erreur lors de l'application des mises à jour : {e}")

if __name__ == "__main__":
    apply_updates()
