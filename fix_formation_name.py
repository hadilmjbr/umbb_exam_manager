
from backend.db import get_connection

def fix_formation():
    conn = get_connection()
    cur = conn.cursor()
    
    # Check for L1 Chimie
    cur.execute("SELECT id FROM formations WHERE nom = 'L1 Chimie'")
    l1_chimie = cur.fetchone()
    
    # Check for L1 SM
    cur.execute("SELECT id FROM formations WHERE nom = 'L1 Sciences de la Matière'")
    l1_sm = cur.fetchone()
    
    if l1_chimie and l1_sm:
        print(f"Both exist. L1 Chimie ID: {l1_chimie[0]}, L1 SM ID: {l1_sm[0]}")
        # Move any students/modules from L1 Chimie to L1 SM
        cur.execute("UPDATE modules SET formation_id = %s WHERE formation_id = %s", (l1_sm[0], l1_chimie[0]))
        cur.execute("UPDATE etudiants SET formation_id = %s WHERE formation_id = %s", (l1_sm[0], l1_chimie[0]))
        
        # Delete L1 Chimie
        cur.execute("DELETE FROM formations WHERE id = %s", (l1_chimie[0],))
        print("Merged L1 Chimie into L1 SM and deleted L1 Chimie.")
        
    elif l1_chimie and not l1_sm:
        # Just rename
        cur.execute("UPDATE formations SET nom = 'L1 Sciences de la Matière' WHERE id = %s", (l1_chimie[0],))
        print("Renamed L1 Chimie to L1 Sciences de la Matière.")
        
    else:
        print("L1 Sciences de la Matière already exists and L1 Chimie is gone.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_formation()
