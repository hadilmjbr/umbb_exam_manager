from backend.db import get_connection
import sys

try:
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        print("--- TABLES START ---")
        for t in tables:
            print(t[0])
        print("--- TABLES END ---")
        cur.close()
        conn.close()
    else:
        print("Failed to connect")
except Exception as e:
    print(f"Error: {e}")
