"""
Simple script to show what's really in the database
"""
from backend.db import get_connection

conn = get_connection()
if conn:
    cur = conn.cursor()
    
    # Show all users with their emails
    print("ALL USERS IN DATABASE:")
    print("-" * 80)
    cur.execute("SELECT id, username, email, role FROM users ORDER BY id LIMIT 20")
    for row in cur.fetchall():
        print(f"ID:{row[0]:3} | Username:{row[1]:25} | Email:{row[2]:35} | Role:{row[3]}")
    
    print("\n" + "-" * 80)
    
    # Count users with vs without email
    cur.execute("SELECT COUNT(*) FROM users WHERE email IS NOT NULL AND email != ''")
    with_email = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    
    print(f"\nTotal users: {total}")
    print(f"With email: {with_email}")
    print(f"Without email: {total - with_email}")
    
    conn.close()
else:
    print("Connection failed")
