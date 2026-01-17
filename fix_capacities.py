from backend.db import get_connection

def fix_room_capacities():
    print("🔧 Correction des capacités des salles...")
    
    conn = get_connection()
    if not conn:
        print("❌ Echec connexion")
        return

    cur = conn.cursor()
    
    try:
        # 1. Update Amphis to 400 (Realistic for L1/L2)
        print("   - Mise à jour Amphis -> 400 places")
        cur.execute("""
            UPDATE salles 
            SET capacite = 400 
            WHERE type = 'Amphis' OR nom LIKE 'Amphi%'
        """)
        
        # 2. Update some large classrooms if needed (Bloc 1 usually large)
        print("   - Mise à jour Salles Bloc 1 -> 80 places")
        cur.execute("""
            UPDATE salles 
            SET capacite = 80 
            WHERE bloc = 'Bloc 1'
        """)
        
        conn.commit()
        print("✅ Mises à jour effectuées avec succès.")
        
        # Verification
        cur.execute("SELECT nom, capacite FROM salles WHERE type='Amphis' LIMIT 3")
        print("   Exemple vérification:", cur.fetchall())
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_room_capacities()
