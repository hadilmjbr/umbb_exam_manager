"""
Migration script to add email column and populate emails for existing users.
Run this ONCE to migrate from username-only to email authentication.
"""
from backend.db import get_connection
import hashlib

def add_email_column():
    """Add email column to users table if it doesn't exist."""
    conn = get_connection()
    if not conn:
        print("❌ Cannot connect to database")
        return False
   
    try:
        cur = conn.cursor()
        
        # Add email column
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS email VARCHAR(150)
        """)
        
        conn.commit()
        print("✅ Email column added/verified")
        return True
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        return False
    finally:
        conn.close()

def populate_emails():
    """Populate email addresses for existing users."""
    conn = get_connection()
    if not conn:
        print("❌ Cannot connect to database")
        return False
    
    try:
        cur = conn.cursor()
        
        # Get all users
        cur.execute("SELECT id, username, role, ref_id FROM users WHERE email IS NULL OR email = ''")
        users = cur.fetchall()
        
        updated = 0
        for user_id, username, role, ref_id in users:
            email = None
            
            if role == 'ADMIN':
                email = 'admin@umbb.dz'
            elif role == 'DOYEN':
                email = 'doyen@umbb.dz'
            elif role == 'CHEF':
                # chef_informatique -> chef.informatique@umbb.dz
                clean_name = username.replace('chef_', '')
                email = f"chef.{clean_name}@umbb.dz"
            elif role in ['PROF', 'ETUDIANT']:
                # username is already prenom.nom format
                email = f"{username}@umbb.dz"
            
            if email:
                cur.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
                updated += 1
        
        conn.commit()
        print(f"✅ Updated {updated} users with email addresses")
        
        # Add unique constraint
        try:
            cur.execute("ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email)")
            print("✅ Added unique constraint on email")
        except:
            print("⚠️ Unique constraint already exists or couldn't be added")
        
        conn.commit()
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error populating emails: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting email migration...")
    if add_email_column():
        if populate_emails():
            print("\n✅ Migration completed successfully!")
            print("\nYou can now login with:")
            print("  Admin: admin@umbb.dz / admin123")
            print("  Doyen: doyen@umbb.dz / 123456")
            print("  Chef: chef.informatique@umbb.dz / 123456")
            print("  Others: prenom.nom@umbb.dz / 123456")
        else:
            print("\n❌ Migration failed at email population step")
    else:
        print("\n❌ Migration failed at column addition step")
