from backend.db import get_connection

def find_target_formations():
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    
    depts = [
        (1, "Informatique"),
        (2, "Mathématiques"),
        (3, "Physique"),
        (4, "Chimie"),
        (5, "SNV"),
        (6, "STAPS"),
        (7, "Médecine")
    ]
    
    print("RECHERCHE DES FORMATIONS CIBLES :")
    for d_id, d_nom in depts:
        # Search by ID or Name
        cur.execute("SELECT id, nom FROM formations WHERE dept_id = %s OR nom ILIKE %s LIMIT 1", (d_id, f"%{d_nom}%"))
        res = cur.fetchone()
        if res:
            print(f"Propriété {d_nom} (Dept {d_id}) -> Formation ID {res[0]} ({res[1]})")
        else:
            print(f"❌ {d_nom} NON TROUVÉ")
            
    conn.close()

if __name__ == "__main__":
    find_target_formations()
