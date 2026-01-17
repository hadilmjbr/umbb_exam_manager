"""
Direct test of authentication with comprehensive debugging
"""
from backend.db import get_connection
from backend.auth import hash_password, verify_user

print("="*60)
print("AUTHENTICATION TEST")
print("="*60)

# Test 1: Check database connection
print("\n1️⃣ Testing database connection...")
conn = get_connection()
if conn:
    print("✅ Database connected")
    
    # Test 2: Check table structure
    print("\n2️⃣ Checking users table structure...")
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in cur.fetchall()]
    print(f"   Columns: {', '.join(columns)}")
    
    if 'email' not in columns:
        print("   ❌ EMAIL COLUMN MISSING!")
    else:
        print("   ✅ Email column exists")
    
    # Test 3: Check admin user
    print("\n3️⃣ Checking admin user...")
    cur.execute("SELECT id, username, email, role FROM users WHERE username = 'admin'")
    admin = cur.fetchone()
    if admin:
        print(f"   ID: {admin[0]}")
        print(f"   Username: {admin[1]}")
        print(f"   Email: {admin[2]}")
        print(f"   Role: {admin[3]}")
        
        if not admin[2] or admin[2] == '':
            print("   ❌ EMAIL IS EMPTY!")
        else:
            print(f"   ✅ Email is set: {admin[2]}")
    else:
        print("   ❌ Admin user not found!")
    
    # Test 4: Try authentication with email
    print("\n4️⃣ Testing authentication...")
    test_email = "admin@umbb.dz"
    test_password = "admin123"
    
    print(f"   Trying: {test_email} / {test_password}")
    
    # Manual query
    pwd_hash = hash_password(test_password)
    cur.execute("""
        SELECT id, username, email, role, ref_id 
        FROM users 
        WHERE email = %s AND password_hash = %s
    """, (test_email, pwd_hash))
    
    result = cur.fetchone()
    if result:
        print(f"   ✅ Manual query SUCCESS: {result}")
    else:
        print(f"   ❌ Manual query FAILED")
        
        # Check if email exists
        cur.execute("SELECT id, email FROM users WHERE email = %s", (test_email,))
        email_check = cur.fetchone()
        if email_check:
            print(f"      Email exists: {email_check}")
            print(f"      → Password hash mismatch!")
        else:
            print(f"      Email does NOT exist in database")
    
    # Test via function
    print("\n5️⃣ Testing verify_user function...")
    user_data = verify_user(test_email, test_password)
    if user_data:
        print(f"   ✅ Function SUCCESS: {user_data}")
    else:
        print(f"   ❌ Function FAILED")
    
    conn.close()
else:
    print("❌ Cannot connect to database")

print("\n" + "="*60)
