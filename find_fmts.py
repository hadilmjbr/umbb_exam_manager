from backend.db import get_connection

def find_formations():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, nom FROM formations ORDER BY nom")
    results = cur.fetchall()
    
    print("--- ALL FORMATIONS ---")
    for r in results:
        print(r)
    
    conn.close()

if __name__ == "__main__":
    find_formations()
