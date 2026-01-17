import sys
import os

sys.path.append(os.getcwd())

from backend.db import get_connection

def init_inscriptions():
    conn = get_connection()
    if not conn:
        print("No connection")
        return

    cur = conn.cursor()
    
    # Create table
    print("Creating inscriptions table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inscriptions (
            id SERIAL PRIMARY KEY,
            etudiant_id INTEGER REFERENCES etudiants(id),
            module_id INTEGER REFERENCES modules(id),
            UNIQUE(etudiant_id, module_id)
        );
    """)
    conn.commit()

    # Populate
    print("Populating inscriptions...")
    # Logic: Insert (etudiant_id, module_id) where etudiant.formation_id == module.formation_id
    cur.execute("""
        INSERT INTO inscriptions (etudiant_id, module_id)
        SELECT e.id, m.id
        FROM etudiants e
        JOIN modules m ON e.formation_id = m.formation_id
        ON CONFLICT (etudiant_id, module_id) DO NOTHING;
    """)
    
    count = cur.rowcount
    conn.commit()
    print(f"Inserted {count} inscriptions.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_inscriptions()
