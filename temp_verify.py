from backend.db import get_connection

def verify_data():
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    
    # Check for 'Test'
    cur.execute("SELECT COUNT(*) FROM etudiants WHERE nom ILIKE '%Test%' OR prenom ILIKE '%Test%'")
    e_test = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM professeurs WHERE nom ILIKE '%Test%'")
    p_test = cur.fetchone()[0]
    
    # Check room count
    cur.execute("SELECT COUNT(*) FROM salles WHERE type='Salle'")
    s_count = cur.fetchone()[0]
    
    # Check amphi capacity
    cur.execute("SELECT MIN(capacite), MAX(capacite) FROM salles WHERE type='Amphi'")
    a_cap = cur.fetchone()
    
    print(f"ETU_TEST_COUNT={e_test}")
    print(f"PROF_TEST_COUNT={p_test}")
    print(f"SALLE_COUNT={s_count}")
    print(f"AMPHI_CAP_MIN={a_cap[0]}")
    print(f"AMPHI_CAP_MAX={a_cap[1]}")
    
    conn.close()

if __name__ == '__main__':
    verify_data()
