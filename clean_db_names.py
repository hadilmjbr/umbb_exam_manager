from backend.db import get_connection

def clean_database():
    print("🧹 Nettoyage de la base de données (suppression de 'Test')...")
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    
    try:
        # Nettoyage des prénoms et noms
        cur.execute("UPDATE etudiants SET prenom = TRIM(REPLACE(prenom, 'Test', '')), nom = TRIM(REPLACE(nom, 'Etudiant', '')) WHERE prenom LIKE '%Test%' OR nom LIKE '%Etudiant%'")
        cur.execute("UPDATE etudiants SET nom = 'Informatique' WHERE nom = 'Informatique' AND prenom = ''") # Cleanup specific case if needed
        
        # On renomme proprement les comptes de test si besoin
        cur.execute("UPDATE etudiants SET nom = 'Informatique', prenom = 'Étudiant' WHERE nom = 'Etudiant Informatique'")
        cur.execute("UPDATE etudiants SET nom = 'Mathématiques', prenom = 'Étudiant' WHERE nom = 'Etudiant Math'")
        cur.execute("UPDATE etudiants SET nom = 'Physique', prenom = 'Étudiant' WHERE nom = 'Etudiant Physique'")
        cur.execute("UPDATE etudiants SET nom = 'Chimie', prenom = 'Étudiant' WHERE nom = 'Etudiant Chimie'")
        cur.execute("UPDATE etudiants SET nom = 'SNV', prenom = 'Étudiant' WHERE nom = 'Etudiant SNV'")
        cur.execute("UPDATE etudiants SET nom = 'STAPS', prenom = 'Étudiant' WHERE nom = 'Etudiant STAPS'")
        cur.execute("UPDATE etudiants SET nom = 'Médecine', prenom = 'Étudiant' WHERE nom = 'Etudiant Medecine'")
        
        # Etudiants normaux
        cur.execute("UPDATE etudiants SET prenom = REPLACE(prenom, 'Test', '') WHERE prenom LIKE '%Test%'")
        
        conn.commit()
        print("✅ Nettoyage terminé.")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_database()
