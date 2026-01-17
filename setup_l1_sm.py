import random
from backend.db import get_connection

def setup_data():
    conn = get_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        
        # --- 1. L1 Sciences de la Matière ---
        print("--- Setting up L1 SM ---")
        # Check if exists
        cur.execute("SELECT id FROM formations WHERE nom = 'L1 Sciences de la Matière'")
        row = cur.fetchone()
        if row:
            l1_sm_id = row[0]
            print(f"ℹ️ Found L1 SM (ID: {l1_sm_id})")
        else:
            # Create linked to Chimie (Dept 4)
            cur.execute("INSERT INTO formations (nom, dept_id) VALUES ('L1 Sciences de la Matière', 4) RETURNING id")
            l1_sm_id = cur.fetchone()[0]
            print(f"✅ Created L1 SM (ID: {l1_sm_id})")
            
        # Create Modules
        modules = ['Analyse 1', 'Algèbre 1', 'Physique Générale', 'Chimie Générale', 'Informatique 1', 'Anglais 1']
        module_ids = []
        for mod_name in modules:
            cur.execute("SELECT id FROM modules WHERE nom = %s AND formation_id = %s", (mod_name, l1_sm_id))
            row = cur.fetchone()
            if row:
                module_ids.append(row[0])
            else:
                cur.execute("INSERT INTO modules (nom, formation_id) VALUES (%s, %s) RETURNING id", (mod_name, l1_sm_id))
                mid = cur.fetchone()[0]
                module_ids.append(mid)
                print(f"   + Added module {mod_name}")
                
        # Link Test Students to L1 SM
        # Oulebsir Katia (Chimie) & Rezzik Ameyas (Physique) -> L1 SM
        cur.execute("UPDATE etudiants SET formation_id = %s WHERE nom = 'Oulebsir' AND prenom = 'Katia'", (l1_sm_id,))
        cur.execute("UPDATE etudiants SET formation_id = %s WHERE nom = 'Rezzik' AND prenom = 'Ameyas'", (l1_sm_id,))
        print("✅ Linked test students to L1 SM")

        # --- 2. Fix Professor Schedules ---
        print("--- Assigning Exams to Test Profs ---")
        # Get IDs of prof1..prof5
        prof_emails = [f"prof{i}@gmail.com" for i in range(1, 6)]
        prof_map = {} # email -> id
        for email in prof_emails:
            cur.execute("SELECT id, username FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            if row:
                prof_map[email] = row[0]
        
        # Get some exams
        cur.execute("SELECT id FROM examens ORDER BY date_heure LIMIT 20")
        exam_ids = [r[0] for r in cur.fetchall()]
        
        if not exam_ids:
            print("⚠️ No exams found to assign!")
        else:
            # Distribute exams to profs
            # We update the 'prof_id' of existing exams to be one of our test profs
            # This 'steals' exams from original profs but ensures our test users have data.
            # Only do this if they don't have exams? Or just overwrite specific ones?
            # Let's overwrite a few for each.
            
            idx = 0
            for email, pid in prof_map.items():
                if idx < len(exam_ids):
                    # Assign 2 exams per prof
                    ex1 = exam_ids[idx]
                    ex2 = exam_ids[(idx+1) % len(exam_ids)]
                    cur.execute("UPDATE examens SET prof_id = %s WHERE id IN (%s, %s)", (pid, ex1, ex2))
                    print(f"   -> Assigned exams {ex1}, {ex2} to {email} (ID: {pid})")
                    idx += 2
        
        conn.commit()
        print("✅ Database setup complete.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    setup_data()
