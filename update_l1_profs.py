import hashlib
from backend.db import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def update_data():
    conn = get_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        
        # 1. Add L1 Chimie
        # Check if it exists
        cur.execute("SELECT id FROM formations WHERE nom = 'L1 Chimie'")
        if cur.fetchone():
            print("ℹ️ 'L1 Chimie' already exists.")
        else:
            # Insert linked to Dept 4 (Chimie)
            cur.execute("INSERT INTO formations (nom, dept_id) VALUES ('L1 Chimie', 4) RETURNING id")
            new_id = cur.fetchone()[0]
            print(f"✅ Added 'L1 Chimie' (ID: {new_id})")
            
        # 2. Update Profs to prof1..prof5
        # Get 5 profs
        cur.execute("SELECT id, username FROM users WHERE role='PROF' ORDER BY id LIMIT 5")
        profs = cur.fetchall()
        
        default_pwd = hash_password("123456")
        
        for i, (uid, old_user) in enumerate(profs, 1):
            new_email = f"prof{i}@gmail.com"
            new_user = f"prof{i}"
            
            # Update user
            cur.execute("""
                UPDATE users 
                SET email = %s, username = %s, password_hash = %s 
                WHERE id = %s
            """, (new_email, new_user, default_pwd, uid))
            print(f"✅ Updated Prof {uid}: {new_email} / 123456")
            
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_data()
