from backend.db import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_students():
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    
    password_hash = hash_password("123456")
    
    test_data = [
        {"email": "etudiantinformatique@gmail.com", "nom": "Etudiant Informatique", "dept": "Informatique", "username": "etud_info"},
        {"email": "etudiantmath@gmail.com", "nom": "Etudiant Math", "dept": "Mathematiques", "username": "etud_math"},
        {"email": "etudiantphysique@gmail.com", "nom": "Etudiant Physique", "dept": "Physique", "username": "etud_physique"},
        {"email": "etudiantchimie@gmail.com", "nom": "Etudiant Chimie", "dept": "Chimie", "username": "etud_chimie"},
        {"email": "etudiantsnv@gmail.com", "nom": "Etudiant SNV", "dept": "Sciences de la Nature", "username": "etud_snv"},
        {"email": "etudiantstaps@gmail.com", "nom": "Etudiant STAPS", "dept": "STAPS", "username": "etud_staps"},
        {"email": "etudiantmedecine@gmail.com", "nom": "Etudiant Medecine", "dept": "Medecine", "username": "etud_medecine"}
    ]
    
    print("🚀 Création des comptes étudiants de test...")
    
    for data in test_data:
        # Finding a formation for this department
        cur.execute("""
            SELECT f.id, f.nom 
            FROM formations f 
            JOIN departements d ON f.dept_id = d.id 
            WHERE d.nom ILIKE %s 
            LIMIT 1
        """, (f"%{data['dept']}%",))
        fmt = cur.fetchone()
        
        if not fmt:
            print(f"❌ Département {data['dept']} non trouvé.")
            continue
            
        fmt_id, fmt_nom = fmt
        
        # 1. Create Student entry
        cur.execute("""
            INSERT INTO etudiants (nom, prenom, formation_id, annee_univ)
            VALUES (%s, '', %s, '2025-2026')
            RETURNING id
        """, (data['nom'], fmt_id))
        etudiant_id = cur.fetchone()[0]
        
        # 2. Create User account
        cur.execute("""
            INSERT INTO users (username, password_hash, role, ref_id, email)
            VALUES (%s, %s, 'ETUDIANT', %s, %s)
            ON CONFLICT (email) DO UPDATE SET 
                password_hash = EXCLUDED.password_hash,
                ref_id = EXCLUDED.ref_id,
                username = EXCLUDED.username
        """, (data['username'], password_hash, etudiant_id, data['email']))
        
        # 3. Add inscriptions to ensure they have an EDT
        cur.execute("SELECT id FROM modules WHERE formation_id = %s", (fmt_id,))
        modules = cur.fetchall()
        for mod in modules:
            cur.execute("""
                INSERT INTO inscriptions (etudiant_id, module_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (etudiant_id, mod[0]))
            
        print(f"✅ Créé : {data['email']} -> {fmt_nom} (ID Dept: {data['dept']})")

    conn.commit()
    cur.close()
    conn.close()
    print("\n🎉 Tous les comptes de test sont créés !")

if __name__ == "__main__":
    create_test_students()
