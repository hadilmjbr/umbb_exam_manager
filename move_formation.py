
from backend.db import get_connection

def move_formation():
    conn = get_connection()
    if not conn:
        print("DB Connection failed")
        return

    cur = conn.cursor()
    
    # 1. Get Physique ID
    cur.execute("SELECT id FROM departements WHERE nom LIKE '%Physique%'")
    phys_res = cur.fetchone()
    if not phys_res:
        print("Physique dept not found!")
        return
    phys_id = phys_res[0]
    print(f"Dept Physique ID: {phys_id}")

    # 2. Get L1 SM ID
    cur.execute("SELECT id, nom, dept_id FROM formations WHERE nom LIKE '%Sciences%Matière%'")
    fmt_res = cur.fetchone()
    if not fmt_res:
        print("Formation L1 Sciences de la Matière not found!")
        return
    fmt_id = fmt_res[0]
    old_dept_id = fmt_res[2]
    print(f"Formation ID: {fmt_id}, Current Dept: {old_dept_id}")

    # 3. Update
    cur.execute("UPDATE formations SET dept_id = %s WHERE id = %s", (phys_id, fmt_id))
    conn.commit()
    print(f"Updated L1 SM to Dept {phys_id}.")
    
    conn.close()

if __name__ == "__main__":
    move_formation()
