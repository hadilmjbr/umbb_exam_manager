import hashlib
from backend.db import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def force_standardize():
    conn = get_connection()
    if not conn:
        print("Failed to connect")
        return
    try:
        cur = conn.cursor()
        
        # 0. Check for existing users with gmail to see if we have duplicates
        print("--- Cleaning up problematic records ---")
        cur.execute("DELETE FROM users WHERE email LIKE '%@umbb.dz%' AND username IN ('admin', 'doyen')")
        
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
        
        # Verify immediately
        cur.execute("SELECT username, email FROM users WHERE username IN ('admin', 'doyen')")
        print("Verification (Admin/Doyen):", cur.fetchall())
        
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
                SET email = EXCLUDED.email, password_hash = EXCLUDED.password_hash
            """, (username, email, default_pass, d_id))
            
        print("--- Forcing all roles to gmail if they match patterns ---")
        # Aggressive update for all @umbb.dz emails
        cur.execute("UPDATE users SET email = REPLACE(email, '@umbb.dz', '@gmail.com') WHERE email LIKE '%@umbb.dz'")
        
        print("--- Adding Test Students ---")
        test_students = [
            ("Medjber", "Hadil", "medjberhadil@gmail.com", "hadil2026", 4),
            ("Oulebsir", "Katia", "oulebsirkatia@gmail.com", "katia2026", 38),
            ("Rezzik", "Ameyas", "rezzikameyas@gmail.com", "ameyas2026", 21)
        ]
        for nom, prenom, email, pwd, fmt_id in test_students:
            cur.execute("SELECT id FROM etudiants WHERE nom = %s AND prenom = %s", (nom, prenom))
            row = cur.fetchone()
            if not row:
                cur.execute("INSERT INTO etudiants (nom, prenom, formation_id) VALUES (%s, %s, %s) RETURNING id", (nom, prenom, fmt_id))
                st_id = cur.fetchone()[0]
            else:
                st_id = row[0]
            
            p_hash = hash_password(pwd)
            username = f"{nom.lower()}{prenom.lower()}"
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'ETUDIANT', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email, password_hash = EXCLUDED.password_hash
            """, (username, email, p_hash, st_id))

        conn.commit()
        print("✅ Database updated and committed.")
        
        # Final Verification
        cur.execute("SELECT role, email FROM users WHERE role IN ('ADMIN', 'DOYEN')")
        print("Final check (Roles):", cur.fetchall())
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    force_standardize()
