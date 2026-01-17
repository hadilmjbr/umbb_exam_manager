"""
Fixed migration: Properly add email column and populate all users
"""
from backend.db import get_connection

def migrate_emails():
    conn = get_connection()
    if not conn:
        print("❌ Cannot connect to database")
        return False
    
    try:
        cur = conn.cursor()
        
        # Step 1: Add column if doesn't exist (drop constraint first if exists)
        print("Step 1: Adding email column...")
        try:
            cur.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_unique")
            conn.commit()
        except:
            pass
            
        try:
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(150)")
            conn.commit()
            print("✅ Email column added")
        except Exception as e:
            print(f"⚠️ Column might already exist: {e}")
            conn.rollback()
        
        # Step 2: Update all existing users with emails
        print("\nStep 2: Populating emails...")
        
        # Get all users
        cur.execute("SELECT id, username, role FROM users")
        users = cur.fetchall()
        
        updated = 0
        for user_id, username, role in users:
            email = None
            
            if username == 'admin':
                email = 'admin@umbb.dz'
            elif username == 'doyen':
                email = 'doyen@umbb.dz'
            elif username.startswith('chef_'):
                # chef_informatique -> chef.informatique@umbb.dz
                dept = username.replace('chef_', '')
                email = f"chef.{dept}@umbb.dz"
            else:
                # For prof and students: username is already prenom.nom
                email = f"{username}@umbb.dz"
            
            if email:
                cur.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
                updated += 1
                print(f"  Updated {username} -> {email}")
        
        conn.commit()
        print(f"\n✅ Updated {updated} users")
        
        # Step 3: Make email NOT NULL and UNIQUE
        print("\nStep 3: Adding constraints...")
        try:
            cur.execute("ALTER TABLE users ALTER COLUMN email SET NOT NULL")
            print("✅ Set email as NOT NULL")
        except Exception as e:
            print(f"⚠️ NOT NULL constraint: {e}")
            conn.rollback()
            
        try:
            cur.execute("ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email)")
            print("✅ Added UNIQUE constraint")
        except Exception as e:
            print(f"⚠️ UNIQUE constraint: {e}")
        
        conn.commit()
        
        # Step 4: Verify
        print("\nStep 4: Verification...")
        cur.execute("SELECT username, email, role FROM users LIMIT 5")
        print("Sample users:")
        for row in cur.fetchall():
            print(f"  {row[0]} | {row[1]} | {row[2]}")
        
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*50)
    print("MIGRATION: Adding emails to users table")
    print("="*50)
    if migrate_emails():
        print("\n" + "="*50)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("="*50)
        print("\n📧 You can now login with:")
        print("  • Admin: admin@umbb.dz / admin123")
        print("  • Doyen: doyen@umbb.dz / 123456")
        print("  • Chef Informatique: chef.informatique@umbb.dz / 123456")
        print("  • Others: prenom.nom@umbb.dz / 123456")
    else:
        print("\n❌ MIGRATION FAILED")
