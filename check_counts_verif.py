from backend.db import get_connection

tables = ['examens', 'modules', 'formations', 'salles', 'professeurs', 'etudiants', 'inscriptions']
conn = get_connection()
if conn:
    cur = conn.cursor()
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"{t}: {cur.fetchone()[0]}")
        except Exception as e:
            print(f"{t}: Error {e}")
    cur.close()
    conn.close()
