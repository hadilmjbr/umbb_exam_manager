from backend.db import get_connection
import pandas as pd

def run_audit():
    print("="*60)
    print("🔍 RAPPORT DE VÉRIFICATION FINALE DU PROJET")
    print("="*60)
    
    conn = get_connection()
    if not conn:
        print("❌ Erreur de connexion à la BDD")
        return
    cur = conn.cursor()
    
    # 1. Vérification des Salles
    print("\n[1] ARCHITECTURE DES SALLES")
    cur.execute("SELECT COUNT(*) FROM salles WHERE type='Salle'")
    count = cur.fetchone()[0]
    print(f"  - Total Salles Bloc: {count} (Attendu: 180)")
    
    cur.execute("SELECT bloc, COUNT(*) FROM salles WHERE type='Salle' GROUP BY bloc ORDER BY bloc")
    blocs = cur.fetchall()
    print(f"  - Répartition par Bloc: {dict(blocs)}")
    
    # 2. Vérification du Workflow de Publication
    print("\n[2] WORKFLOW DE VALIDATION")
    cur.execute("SELECT statut, COUNT(*) FROM validation_pedagogique GROUP BY statut")
    stats = cur.fetchall()
    print(f"  - État des EDT: {dict(stats)}")
    
    # 3. Vérification de l'Invisibilité (Sécurité)
    print("\n[3] SÉCURITÉ DE VISIBILITÉ")
    from backend.public import get_formation_exams_public
    # On cherche une formation qui n'est pas PUBLIE
    cur.execute("SELECT formation_id FROM validation_pedagogique WHERE statut != 'PUBLIE' LIMIT 1")
    row = cur.fetchone()
    if row:
        fmt_id = row[0]
        exams = get_formation_exams_public(fmt_id)
        print(f"  - Test Visibilité (Formation non publiée ID {fmt_id}): {len(exams)} examens visibles (Attendu: 0)")
    else:
        print("  - Aucune formation non-publiée pour tester, vérification manuelle du code...")

    # 4. Vérification du code critique (Vérification par lecture)
    print("\n[4] AUDIT DU CODE CRITIQUE")
    with open('backend/public.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if "v.statut = 'PUBLIE'" in content:
            print("  - ✅ Filtre 'statut = PUBLIE' détecté dans backend/public.py")
        else:
            print("  - ❌ Filtre 'statut = PUBLIE' MANQUANT dans backend/public.py")
            
    with open('backend/admin.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if "publish_directly" not in content:
            print("  - ✅ Fonction bypass 'publish_directly' supprimée de backend/admin.py")
        else:
            print("  - ❌ Fonction bypass 'publish_directly' toujours présente !")

    # 5. Propreté des noms
    print("\n[5] PROPRETÉ DES NOMS")
    cur.execute("SELECT COUNT(*) FROM etudiants WHERE nom ILIKE '%Test%' OR prenom ILIKE '%Test%'")
    test_count = cur.fetchone()[0]
    print(f"  - Mots 'Test' restants dans les noms: {test_count} (Attendu: 0)")

    conn.close()
    print("\n" + "="*60)
    print("✅ VÉRIFICATION TERMINÉE - AUCUNE MODIFICATION EFFECTUÉE")

if __name__ == "__main__":
    run_audit()
