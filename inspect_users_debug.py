from backend.db import get_connection

def inspect_users():
    conn = get_connection()
    if not conn:
        print("Failed to connect")
        return
    try:
        cur = conn.cursor()
        print("--- DOYEN & CHEFS ---")
        cur.execute("SELECT id, username, email, role, ref_id FROM users WHERE role IN ('DOYEN', 'CHEF')")
        rows = cur.fetchall()
        print(f"Total Doyen/Chefs found: {len(rows)}")
        for row in rows:
            print(row)
        
        print("\n--- ADMIN ---")
        cur.execute("SELECT id, username, email, role, ref_id FROM users WHERE role = 'ADMIN'")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            
        print("\n--- STUDENTS ---")
        cur.execute("SELECT id, nom, prenom, email, formation_id FROM etudiants LIMIT 5")
        rows = cur.fetchall()
        for row in rows:
            print(row)

        print("\n--- ROLES COUNT ---")
        cur.execute("SELECT role, count(*) FROM users GROUP BY role")
        for row in cur.fetchall():
            print(row)

    finally:
        conn.close()

if __name__ == "__main__":
    inspect_users()
