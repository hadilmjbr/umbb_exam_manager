from backend.db import get_connection

def list_all_users():
    conn = get_connection()
    if not conn:
        print("Failed to connect")
        return
    cur = conn.cursor()
    cur.execute("SELECT role, email, username FROM users ORDER BY role")
    rows = cur.fetchall()
    print(f"Total users: {len(rows)}")
    for role, email, username in rows:
        if role in ['ADMIN', 'DOYEN', 'CHEF'] or 'medjber' in email or 'oulebsir' in email or 'rezzik' in email:
            print(f"|{role}|{email}|{username}|")
    conn.close()

if __name__ == "__main__":
    list_all_users()
