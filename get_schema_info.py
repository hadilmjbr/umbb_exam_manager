from backend.db import get_connection
import json

tables = ['professeurs', 'salles', 'departements', 'examens']
conn = get_connection()
if conn:
    cur = conn.cursor()
    schema = {}
    for t in tables:
        try:
            cur.execute(f"SELECT * FROM {t} LIMIT 0")
            schema[t] = [desc.name for desc in cur.description]
        except Exception as e:
            schema[t] = str(e)
    print(json.dumps(schema, indent=2))
    cur.close()
    conn.close()
