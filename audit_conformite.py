from backend.db import get_connection
import pandas as pd

def verify_all():
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    
    print("="*50)
    print("📋 AUDIT DE CONFORMITÉ DU PROJET")
    print("="*50)
    
    # 1. Structure des Salles
    print("\n[1] STRUCTURE DES SALLES")
    cur.execute("SELECT COUNT(*) FROM salles WHERE type='Salle'")
    nb_salles = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM salles WHERE type='Amphi'")
    nb_amphis = cur.fetchone()[0]
    print(f"  - Nombre de salles de bloc : {nb_salles} (Attendu: 180)")
    print(f"  - Nombre d'Amphis : {nb_amphis} (Attendu: ~15-17)")
    
    cur.execute("SELECT nom FROM salles WHERE type='Salle' LIMIT 5")
    salle_names = [r[0] for r in cur.fetchall()]
    print(f"  - Format des noms de salles : {salle_names} (Format x.yzz attendu)")
    
    cur.execute("SELECT MIN(capacite), MAX(capacite) FROM salles WHERE type='Salle'")
    cap_salle = cur.fetchone()
    cur.execute("SELECT MIN(capacite), MAX(capacite) FROM salles WHERE type='Amphi'")
    cap_amphi = cur.fetchone()
    print(f"  - Capacité Salles : {cap_salle[0]} à {cap_salle[1]} (Attendu: ~20-35)")
    print(f"  - Capacité Amphis : {cap_amphi[0]} à {cap_amphi[1]} (Attendu: ~50-70)")

    # 2. Workflow de Validation
    print("\n[2] WORKFLOW DE VALIDATION")
    cur.execute("SELECT statut, COUNT(*) FROM validation_pedagogique GROUP BY statut")
    stats = cur.fetchall()
    print(f"  - Répartition des statuts : {stats}")
    
    # 3. Sécurité de Visibilité
    print("\n[3] SÉCURITÉ DE VISIBILITÉ")
    # Simulation d'un prof
    from backend import public
    cur.execute("SELECT id FROM professeurs LIMIT 1")
    p_id = cur.fetchone()[0]
    prof_exams = public.get_professor_exams(p_id)
    print(f"  - Examens visibles par un professeur (sans publication) : {len(prof_exams)} (Attendu: 0)")
    
    # Simulation d'un étudiant
    cur.execute("SELECT formation_id FROM etudiants LIMIT 1")
    f_id = cur.fetchone()[0]
    etu_exams = public.get_formation_exams_public(f_id)
    print(f"  - Examens visibles par un étudiant (sans publication) : {len(etu_exams)} (Attendu: 0)")

    # 4. Intégrité des Données
    print("\n[4] INTÉGRITÉ DES DONNÉES")
    cur.execute("SELECT COUNT(*) FROM etudiants")
    nb_etud = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM inscriptions")
    nb_insc = cur.fetchone()[0]
    print(f"  - Nombre total d'étudiants : {nb_etud}")
    print(f"  - Nombre d'inscriptions : {nb_insc} (Doit être > 0)")
    
    # 5. Comptes de Test
    print("\n[5] COMPTES DE TEST")
    cur.execute("SELECT email FROM users WHERE role='ETUDIANT' AND email LIKE '%@gmail.com' LIMIT 5")
    test_accs = [r[0] for r in cur.fetchall()]
    print(f"  - Comptes tests détectés : {test_accs}")

    conn.close()
    print("\n" + "="*50)
    print("✅ Audit terminé.")

if __name__ == "__main__":
    verify_all()
