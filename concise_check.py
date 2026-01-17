from backend.db import get_connection

def check():
    conn = get_connection()
    cur = conn.cursor()
    
    for table in ['users', 'etudiants']:
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
        cols = [r[0] for r in cur.fetchall()]
        print(f"Table {table}: {cols}")
    
    cur.execute("SELECT id, username, email, role FROM users WHERE role IN ('ADMIN', 'DOYEN')")
    print("Admins/Doyens:", cur.fetchall())
    
    conn.close()

if __name__ == "__main__":
    check()
