from backend.db import get_connection

def check_schema():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM formations LIMIT 0")
    print(f"Formations columns: {[desc[0] for desc in cur.description]}")
    conn.close()

if __name__ == "__main__":
    check_schema()
