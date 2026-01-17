from backend.db import get_connection

tables = ['professeurs', 'salles', 'departements']
conn = get_connection()
if conn:
    cur = conn.cursor()
    for t in tables:
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{t}';")
        cols = cur.fetchall()
        print(f"Table {t}: {[c[0] for c in cols]}")
    cur.close()
    conn.close()
