import hashlib
from backend.db import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(email, password):
    """
    Vérifie les identifiants avec email et retourne les infos utilisateur si valide.
    """
    conn = get_connection()
    if not conn: return None
    
    try:
        cur = conn.cursor()
        pwd_hash = hash_password(password)
        
        cur.execute("""
            SELECT id, username, email, role, ref_id 
            FROM users 
            WHERE email = %s AND password_hash = %s
        """, (email, pwd_hash))
        
        row = cur.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "ref_id": row[4]
            }
        return None
    except Exception as e:
        print(f"Auth Error: {e}")
        return None
    finally:
        conn.close()

def create_users_table():
    """
    Crée la table users si elle n'existe pas.
    """
    conn = get_connection()
    if not conn: return
    
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                role VARCHAR(20) NOT NULL,
                ref_id INTEGER
            )
        """)
        conn.commit()
        print("✅ Table users vérifiée/créée.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def seed_users():
    """
    Migre les professeurs, étudiants et crée les admins/chefs par défaut avec emails.
    """
    conn = get_connection()
    if not conn: return
    
    try:
        cur = conn.cursor()
        
        # 1. Admin
        admin_pass = hash_password("admin123")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, ref_id)
            VALUES ('admin', 'admin@umbb.dz', %s, 'ADMIN', NULL)
            ON CONFLICT (username) DO UPDATE 
            SET email = 'admin@umbb.dz'
        """, (admin_pass,))
        
        # 1b. Doyen
        doyen_pass = hash_password("123456")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, ref_id)
            VALUES ('doyen', 'doyen@umbb.dz', %s, 'DOYEN', NULL)
            ON CONFLICT (username) DO UPDATE 
            SET email = 'doyen@umbb.dz'
        """, (doyen_pass,))
        
        # 2. Chefs de Dept
        default_pass = hash_password("123456")
        
        cur.execute("SELECT id, nom FROM departements")
        depts = cur.fetchall()
        for d_id, d_nom in depts:
            # Username: chef_chimie, chef_info...
            clean_nom = d_nom.lower().replace(" ", "").replace("é", "e").replace("è", "e")
            username = f"chef_{clean_nom}"
            email = f"chef.{clean_nom}@umbb.dz"
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'CHEF', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email
            """, (username, email, default_pass, d_id))
            
        # 3. Professeurs
        try:
            # Try with prenom first
            cur.execute("SELECT id, nom, prenom FROM professeurs")
        except:
            conn.rollback()
            cur.execute("SELECT id, nom FROM professeurs")
            
        profs = cur.fetchall()
        for row in profs:
            p_id = row[0]
            p_nom = row[1]
            p_prenom = row[2] if len(row) > 2 else ""
            
            if not p_nom: continue
            
            safe_prenom = p_prenom.lower().replace(" ", "") if p_prenom else "prof"
            safe_nom = p_nom.lower().replace(' ', '').replace('é', 'e').replace('è', 'e')
            username = f"{safe_prenom}.{safe_nom}"
            email = f"{safe_prenom}.{safe_nom}@umbb.dz"
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'PROF', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email
            """, (username, email, default_pass, p_id))

        # 4. Étudiants
        cur.execute("SELECT id, nom, prenom FROM etudiants")
        etus = cur.fetchall()
        for e_id, e_nom, e_prenom in etus:
            if not e_nom or not e_prenom: continue
            safe_prenom = e_prenom.lower().replace(' ', '').replace('é', 'e').replace('è', 'e')
            safe_nom = e_nom.lower().replace(' ', '').replace('é', 'e').replace('è', 'e')
            username = f"{safe_prenom}.{safe_nom}"
            email = f"{safe_prenom}.{safe_nom}@umbb.dz"
            
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role, ref_id)
                VALUES (%s, %s, %s, 'ETUDIANT', %s)
                ON CONFLICT (username) DO UPDATE 
                SET email = EXCLUDED.email
            """, (username, email, default_pass, e_id))

        conn.commit()
        # Check count
        cur.execute("SELECT count(*) FROM users")
        print(f"✅ Total users: {cur.fetchone()[0]}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Seeding Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_users_table()
    seed_users()
