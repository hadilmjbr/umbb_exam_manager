from backend.db import get_connection

conn = get_connection()
if conn:
    cur = conn.cursor()
    for table in ['professeurs', 'modules', 'salles']:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"{table}: {cur.fetchone()[0]}")
    cur.close()
    conn.close()
