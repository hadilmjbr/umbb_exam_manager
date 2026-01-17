from backend.db import get_connection
import pandas as pd

conn = get_connection()
if conn:
    df = pd.read_sql("SELECT nom FROM formations", conn)
    print(df['nom'].tolist())
    conn.close()
