from backend.db import get_connection

def fix_room_capacities_v2():
    print("🔧 Correction des capacités des salles (V2)...")
    
    conn = get_connection()
    if not conn:
        print("❌ Echec connexion")
        return

    cur = conn.cursor()
    
    try:
        # Update based on Name which is clearer
        print("   - Mise à jour Amphis -> 450 places")
        cur.execute("""
            UPDATE salles 
            SET capacite = 450 
            WHERE nom LIKE 'Amphi%'
        """)
        
        # Verify count
        cur.execute("SELECT count(*) FROM salles WHERE capacite = 450")
        cnt = cur.fetchone()[0]
        print(f"   -> {cnt} salles mises à jour à 450 places.")
        
        conn.commit()
        print("✅ Mises à jour effectuées.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_room_capacities_v2()
