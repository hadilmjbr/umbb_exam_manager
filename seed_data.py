from backend.db import get_connection
import random

def seed():
    conn = get_connection()
    if not conn:
        print("No connection")
        return

    cur = conn.cursor()
    
    # 1. Seed Departements
    cur.execute("SELECT COUNT(*) FROM departements")
    if cur.fetchone()[0] == 0:
        print("Seeding departements...")
        depts = ["Informatique", "Mathématiques", "Physique", "Biologie", "Chimie"]
        for d in depts:
            cur.execute("INSERT INTO departements (nom) VALUES (%s)", (d,))
    
    conn.commit()
    
    # Get dept ids
    cur.execute("SELECT id FROM departements")
    dept_ids = [r[0] for r in cur.fetchall()]

    # 2. Seed Professeurs
    cur.execute("SELECT COUNT(*) FROM professeurs")
    if cur.fetchone()[0] == 0:
        print("Seeding professeurs...")
        noms = ["Dupont", "Martin", "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefevre", "Michel", "Garcia"]
        for i, nom in enumerate(noms):
            dept = random.choice(dept_ids) if dept_ids else None
            # Specialite based on department or random
            specialite = "Général"
            cur.execute("INSERT INTO professeurs (nom, dept_id, specialite) VALUES (%s, %s, %s)", (nom, dept, specialite))

    # 3. Seed Salles
    cur.execute("SELECT COUNT(*) FROM salles")
    if cur.fetchone()[0] == 0:
        print("Seeding salles...")
        types = ["Amphi", "TD", "TP"]
        blocs = ["A", "B", "C"]
        for i in range(1, 21):
            nom = f"Salle {i}"
            capacite = random.choice([30, 50, 100, 200])
            typ = random.choice(types)
            bloc = random.choice(blocs)
            cur.execute("INSERT INTO salles (nom, capacite, type, bloc) VALUES (%s, %s, %s, %s)", (nom, capacite, typ, bloc))

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
