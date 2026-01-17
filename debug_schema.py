from backend.db import get_connection
import pandas as pd

conn = get_connection()
if conn:
    try:
        df_p = pd.read_sql("SELECT * FROM professeurs LIMIT 1", conn)
        print("PROFESSEURS COLS:")
        for c in df_p.columns: print(f"- {c}")
        
        df_e = pd.read_sql("SELECT * FROM etudiants LIMIT 1", conn)
        print("ETUDIANTS COLS:")
        for c in df_e.columns: print(f"- {c}")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()
