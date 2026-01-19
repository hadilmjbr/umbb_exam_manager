
import sys
import os

# Add project root to sys path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from backend.db import get_connection
    conn = get_connection()
    if conn:
        print("SUCCESS: Connected to Neon Postgres!")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print(f"Postgres version: {cur.fetchone()}")
        conn.close()
    else:
        print("FAILURE: Could not connect to Neon.")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
