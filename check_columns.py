from backend.db import get_connection

try:
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'salles';")
        cols = cur.fetchall()
        print("--- COLUMNS START ---")
        for c in cols:
            print(c[0])
        print("--- COLUMNS END ---")
        cur.close()
        conn.close()
except Exception as e:
    print(e)
