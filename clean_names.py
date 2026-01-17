from backend.db import get_connection

def clean_formation_names():
    conn = get_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    try:
        cur = conn.cursor()
        
        # Check before
        cur.execute("SELECT count(*) FROM formations WHERE nom LIKE '%(A)%'")
        count_before = cur.fetchone()[0]
        print(f"Found {count_before} formations with '(A)'.")

        if count_before > 0:
            # Update
            # Postgres REPLACE function
            cur.execute("UPDATE formations SET nom = REPLACE(nom, '(A)', '') WHERE nom LIKE '%(A)%'")
            rows_affected = cur.rowcount
            conn.commit()
            print(f"Updated {rows_affected} rows.")
            
            # Additional cleanup for extra spaces if any (e.g. "L3  Info")
            cur.execute("UPDATE formations SET nom = TRIM(nom)")
            conn.commit()
            
        else:
            print("Nothing to clean.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_formation_names()
