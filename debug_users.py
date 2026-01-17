"""
Debug script to check users table and test authentication
"""
from backend.db import get_connection
from backend.auth import hash_password

def check_users():
    conn = get_connection()
    if not conn:
        print("❌ Cannot connect to database")
        return
    
    try:
        cur = conn.cursor()
        
        # Check table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        print("\n📋 Table structure:")
        for col in cur.fetchall():
            print(f"  - {col[0]}: {col[1]}")
        
        # Check users
        cur.execute("SELECT id, username, email, role FROM users LIMIT 10")
        print("\n👥 Sample users:")
        for row in cur.fetchall():
            print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Role: {row[3]}")
        
        # Test admin password hash
        admin_hash = hash_password("admin123")
        cur.execute("SELECT password_hash FROM users WHERE username = 'admin'")
        db_hash = cur.fetchone()
        print(f"\n🔐 Admin password check:")
        print(f"  Expected hash: {admin_hash}")
        print(f"  DB hash: {db_hash[0] if db_hash else 'NOT FOUND'}")
        print(f"  Match: {admin_hash == db_hash[0] if db_hash else False}")
        
        # Test email query
        test_email = "admin@umbb.dz"
        cur.execute("""
            SELECT id, username, email, role, ref_id 
            FROM users 
            WHERE email = %s
        """, (test_email,))
        result = cur.fetchone()
        print(f"\n📧 Email lookup test for '{test_email}':")
        if result:
            print(f"  Found: {result}")
        else:
            print(f"  NOT FOUND")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()
