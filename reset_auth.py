"""
RÉINITIALISATION COMPLÈTE DE L'AUTHENTIFICATION
Ce script va tout réinitialiser et tester
"""
from backend.db import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def reset_all_auth():
    conn = get_connection()
    if not conn:
        print("❌ Connexion impossible")
        return False
    
    try:
        cur = conn.cursor()
        
        print("="*70)
        print("RÉINITIALISATION COMPLÈTE")
        print("="*70)
        
        # 1. Vérifier la structure
        print("\n1️⃣ Vérification de la structure...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = [r[0] for r in cur.fetchall()]
        print(f"   Colonnes: {', '.join(columns)}")
        
        if 'email' not in columns:
            print("   ❌ COLONNE EMAIL MANQUANTE - Ajout...")
            cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(150)")
            conn.commit()
            print("   ✅ Colonne email ajoutée")
        
        # 2. Réinitialiser admin
        print("\n2️⃣ Réinitialisation Admin...")
        admin_hash = hash_password("admin123")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, ref_id)
            VALUES ('admin', 'admin@umbb.dz', %s, 'ADMIN', NULL)
            ON CONFLICT (username) DO UPDATE 
            SET email = 'admin@umbb.dz', password_hash = EXCLUDED.password_hash
        """, (admin_hash,))
        conn.commit()
        print("   ✅ Admin: admin@umbb.dz / admin123")
        
        # 3. Réinitialiser doyen
        print("\n3️⃣ Réinitialisation Doyen...")
        doyen_hash = hash_password("123456")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, ref_id)
            VALUES ('doyen', 'doyen@umbb.dz', %s, 'DOYEN', NULL)
            ON CONFLICT (username) DO UPDATE 
            SET email = 'doyen@umbb.dz', password_hash = EXCLUDED.password_hash
        """, (doyen_hash,))
        conn.commit()
        print("   ✅ Doyen: doyen@umbb.dz / 123456")
        
        # 4. Test authentification DIRECT
        print("\n4️⃣ Test authentification directe...")
        
        # Test admin
        cur.execute("""
            SELECT id, username, email, role 
            FROM users 
            WHERE email = %s AND password_hash = %s
        """, ('admin@umbb.dz', admin_hash))
        
        admin_result = cur.fetchone()
        if admin_result:
            print(f"   ✅ ADMIN OK: {admin_result}")
        else:
            print(f"   ❌ ADMIN ÉCHEC")
            return False
        
        # Test doyen
        cur.execute("""
            SELECT id, username, email, role 
            FROM users 
            WHERE email = %s AND password_hash = %s
        """, ('doyen@umbb.dz', doyen_hash))
        
        doyen_result = cur.fetchone()
        if doyen_result:
            print(f"   ✅ DOYEN OK: {doyen_result}")
        else:
            print(f"   ❌ DOYEN ÉCHEC")
            return False
        
        # 5. Test avec la fonction verify_user
        print("\n5️⃣ Test avec verify_user()...")
        from backend.auth import verify_user
        
        admin_test = verify_user('admin@umbb.dz', 'admin123')
        if admin_test:
            print(f"   ✅ Admin via verify_user: OK")
            print(f"      {admin_test}")
        else:
            print(f"   ❌ Admin via verify_user: ÉCHEC")
        
        doyen_test = verify_user('doyen@umbb.dz', '123456')
        if doyen_test:
            print(f"   ✅ Doyen via verify_user: OK")
        else:
            print(f"   ❌ Doyen via verify_user: ÉCHEC")
        
        conn.close()
        
        print("\n" + "="*70)
        print("✅ RÉINITIALISATION TERMINÉE")
        print("="*70)
        print("\n🔐 UTILISEZ CES IDENTIFIANTS:")
        print("   • admin@umbb.dz / admin123")
        print("   • doyen@umbb.dz / 123456")
        print("\n⚠️  REDÉMARREZ STREAMLIT (Ctrl+C puis relancer)")
        print("="*70)
        
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    reset_all_auth()
