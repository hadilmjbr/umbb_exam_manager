from backend.db import get_connection

def find_info():
    conn = get_connection()
    if not conn:
        print("Failed to connect")
        return
    cur = conn.cursor()
    
    # 1. Get column names for formations
    try:
        cur.execute("SELECT * FROM formations LIMIT 0")
        colnames = [desc[0] for desc in cur.description]
        print(f"Formation Columns: {colnames}")
    except Exception as e:
        print(f"Error checking cols: {e}")
    
    print("--- DEPARTEMENTS ---")
    cur.execute("SELECT id, nom FROM departements WHERE nom ILIKE '%Chimie%' OR nom ILIKE '%Physique%'")
    for r in cur.fetchall():
        print(r)
        
    print("--- FORMATIONS (L1/SM) ---")
    # Assuming 'departement_id' or similar exists based on colnames check, but query broadly first
    cur.execute("SELECT id, nom FROM formations WHERE nom ILIKE '%L1%' OR nom ILIKE '%SM%'")
    for r in cur.fetchall():
        print(r)
        
    print("--- SAMPLE PROFS (For renaming) ---")
    cur.execute("SELECT id, nom, prenom, email FROM users WHERE role = 'PROF' ORDER BY id LIMIT 5")
    for r in cur.fetchall():
        print(r)

    conn.close()

if __name__ == "__main__":
    find_info()
