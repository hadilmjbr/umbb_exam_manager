import hashlib
from backend.db import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def standardize():
    conn = get_connection()
    if not conn:
        print("Failed to connect")
        return
    try:
        cur = conn.cursor()
        
        print("--- Standardizing Admin & Doyen ---")
        admin_pass = hash_password("admin123")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, ref_id)
            VALUES ('admin', 'admin@gmail.com', %s, 'ADMIN', NULL)
            ON CONFLICT (username) DO UPDATE 
            SET email = 'admin@gmail.com', password_hash = EXCLUDED.password_hash
        """, (admin_pass,))
        
        doyen_pass = hash_password("123456")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, ref_id)
            VALUES ('doyen', 'doyen@gmail.com', %s, 'DOYEN', NULL)
            ON CONFLICT (username) DO UPDATE 
            SET email = 'doyen@gmail.com', password_hash = EXCLUDED.password_hash
        """, (doyen_pass,))
        
        print("--- Standardizing Chefs ---")
        default_pass = hash_password("123456")
        cur.execute("SELECT id, nom FROM departements")
        depts = cur.fetchall()
        for d_id, d_nom in depts:
            clean_nom = d_nom.lower().strip().replace(" ", "").replace("é", "e").replace("è", "e").replace("ê", "e")
            username = f"chef_{clean_nom}"
            email = f"chef.{clean_nom}@gmail.com"
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'CHEF', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email, password_hash = EXCLUDED.password_hash, ref_id = EXCLUDED.ref_id
            """, (username, email, default_pass, d_id))
            
        print("--- Standardizing Profs ---")
        try:
            cur.execute("SELECT id, nom, prenom FROM professeurs")
            profs = cur.fetchall()
        except:
            conn.rollback()
            cur.execute("SELECT id, nom FROM professeurs")
            profs = [(r[0], r[1], "") for r in cur.fetchall()]
            
        for p_id, p_nom, p_prenom in profs:
            if not p_nom: continue
            safe_prenom = p_prenom.lower().strip().replace(" ", "").replace("é", "e").replace("è", "e").replace("ê", "e") if p_prenom else ""
            safe_nom = p_nom.lower().strip().replace(" ", "").replace("é", "e").replace("è", "e").replace("ê", "e")
            username = f"{safe_nom}{safe_prenom}"
            email = f"{safe_nom}{safe_prenom}@gmail.com"
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'PROF', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email, password_hash = EXCLUDED.password_hash, ref_id = EXCLUDED.ref_id
            """, (username, email, default_pass, p_id))

        print("--- Standardizing Existing Students ---")
        cur.execute("SELECT id, nom, prenom FROM etudiants")
        etus = cur.fetchall()
        for e_id, e_nom, e_prenom in etus:
            if not e_nom or not e_prenom: continue
            safe_prenom = e_prenom.lower().strip().replace(" ", "").replace("é", "e").replace("è", "e").replace("ê", "e")
            safe_nom = e_nom.lower().strip().replace(" ", "").replace("é", "e").replace("è", "e").replace("ê", "e")
            username = f"{safe_nom}{safe_prenom}"
            email = f"{safe_nom}{safe_prenom}@gmail.com"
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'ETUDIANT', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email, password_hash = EXCLUDED.password_hash, ref_id = EXCLUDED.ref_id
            """, (username, email, default_pass, e_id))

        print("--- Adding Test Students ---")
        test_students = [
            ("Medjber", "Hadil", "medjberhadil@gmail.com", "hadil2026", 4),
            ("Oulebsir", "Katia", "oulebsirkatia@gmail.com", "katia2026", 38),
            ("Rezzik", "Ameyas", "rezzikameyas@gmail.com", "ameyas2026", 21)
        ]
        for nom, prenom, email, pwd, fmt_id in test_students:
            cur.execute("SELECT id FROM etudiants WHERE nom = %s AND prenom = %s", (nom, prenom))
            row = cur.fetchone()
            if row:
                st_id = row[0]
            else:
                cur.execute("INSERT INTO etudiants (nom, prenom, formation_id) VALUES (%s, %s, %s) RETURNING id", (nom, prenom, fmt_id))
                st_id = cur.fetchone()[0]
            
            p_hash = hash_password(pwd)
            username = f"{nom.lower()}{prenom.lower()}"
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'ETUDIANT', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email, password_hash = EXCLUDED.password_hash, ref_id = EXCLUDED.ref_id
            """, (username, email, p_hash, st_id))

        conn.commit()
        cur.execute("SELECT count(*) FROM users")
        print(f"✅ Total users: {cur.fetchone()[0]}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    standardize()
