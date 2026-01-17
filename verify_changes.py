
from backend.db import get_connection

def verify():
    conn = get_connection()
    cur = conn.cursor()
    
    print("--- Verification ---")
    
    # 1. Check L1 SM
    cur.execute("SELECT id, dept_id FROM formations WHERE nom = 'L1 Sciences de la Matière'")
    res = cur.fetchone()
    if res and res[1] == 4:
        print("✅ L1 Sciences de la Matière exists and is linked to Chimie (4).")
        l1_id = res[0]
        
        # Check Modules
        cur.execute("SELECT nom FROM modules WHERE formation_id = %s", (l1_id,))
        mods = [r[0] for r in cur.fetchall()]
        expected = ['Analyse 1', 'Algèbre 1', 'Physique Générale', 'Chimie Générale', 'Informatique 1', 'Anglais 1']
        missing = [m for m in expected if m not in mods]
        if not missing:
            print("✅ All expected modules are present.")
        else:
            print(f"❌ Missing modules: {missing}")
            
        # Check Students
        cur.execute("SELECT nom, prenom FROM etudiants WHERE formation_id = %s", (l1_id,))
        students = cur.fetchall()
        print(f"ℹ️ Students in L1 SM: {[f'{s[0]} {s[1]}' for s in students]}")
        
    else:
        print("❌ L1 Sciences de la Matière NOT found or wrong dept.")

    # 2. Check Prof Exams
    cur.execute("SELECT id FROM users WHERE email = 'prof1@gmail.com'")
    prof1_id = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM examens WHERE prof_id = %s", (prof1_id,))
    cnt = cur.fetchone()[0]
    if cnt > 0:
        print(f"✅ prof1@gmail.com has {cnt} exams assigned.")
    else:
        print("❌ prof1@gmail.com has NO exams assigned.")

    conn.close()

if __name__ == "__main__":
    verify()
