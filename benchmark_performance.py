import time
import pandas as pd
from backend.db import get_connection

def benchmark_query(name, query, params=None):
    conn = get_connection()
    if not conn: return
    
    start = time.time()
    try:
        df = pd.read_sql(query, conn, params=params)
        end = time.time()
        duration = end - start
        rows = len(df)
        print(f"⏱️  {name:<40} : {duration:.4f} sec ({rows} rows)")
    except Exception as e:
        print(f"❌ {name:<40} : FAILED ({e})")
    finally:
        conn.close()

def test_trigger_capacity():
    print("\n🔒 Test Trigger Capacité Salle...")
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    
    try:
        # Trouver une petite salle
        cur.execute("SELECT id, capacite FROM salles WHERE capacite < 30 LIMIT 1")
        res = cur.fetchone()
        if not res:
            print("   Pas de petite salle trouvée pour le test.")
            return
        salle_id, cap = res
        
        # Trouver un GROS module
        cur.execute("""
            SELECT m.id, COUNT(i.id) 
            FROM modules m 
            JOIN inscriptions i ON m.id = i.module_id 
            GROUP BY m.id 
            HAVING COUNT(i.id) > %s 
            LIMIT 1
        """, (cap,))
        res_mod = cur.fetchone()
        
        if not res_mod:
            print("   Pas de module avec assez d'inscrits pour déclencher l'erreur.")
            return

        module_id, inscrits = res_mod
        
        print(f"   Tentative: Salle {salle_id} (Cap: {cap}) pour Module {module_id} (Inscrits: {inscrits})")
        
        # Insert qui DOIT échouer
        cur.execute("""
            INSERT INTO examens (module_id, salle_id, date_heure, duree)
            VALUES (%s, %s, NOW(), 90)
        """, (module_id, salle_id))
        
        conn.commit()
        print("❌ LE TRIGGER N'A PAS BLOQUÉ ! (Echec du test)")
        
    except Exception as e:
        print(f"✅ TRIGGER ACTIVÉ : L'insertion a été bloquée comme prévu.\n   Message: {e}")
        conn.rollback()
    finally:
        conn.close()

def run_benchmarks():
    print("="*60)
    print("🚀 BENCHMARK PERFORMANCES SGBD")
    print("="*60)
    
    # 1. KPI Global (Join 4 tables)
    q1 = """
        SELECT d.nom, COUNT(e.id) 
        FROM examens e 
        JOIN modules m ON e.module_id=m.id 
        JOIN formations f ON m.formation_id=f.id 
        JOIN departements d ON f.dept_id=d.id 
        GROUP BY d.nom
    """
    benchmark_query("KPI: Examens par département", q1)

    # 2. Détection Conflits (Produit Cartésien partiel)
    q2 = """
        SELECT COUNT(*) 
        FROM examens e1 
        JOIN examens e2 ON e1.id < e2.id 
        WHERE e1.salle_id = e2.salle_id 
        AND (e1.date_heure, e1.date_heure + (e1.duree || ' minutes')::INTERVAL) 
            OVERLAPS (e2.date_heure, e2.date_heure + (e2.duree || ' minutes')::INTERVAL)
    """
    benchmark_query("Audit: Conflits de salles (Self-Join)", q2)

    # 3. Stats Etudiants (Aggregation massive)
    q3 = """
        SELECT formation_id, COUNT(*) 
        FROM etudiants 
        GROUP BY formation_id
    """
    benchmark_query("Stats: Répartition Étudiants", q3)
    
    # 4. Fonction PL/pgSQL
    conn = get_connection()
    s = time.time()
    cur = conn.cursor()
    cur.execute("SELECT calculer_charge_prof(id) FROM professeurs LIMIT 100")
    cur.fetchall()
    print(f"⏱️  {'PL/pgSQL: 100 appels de fonction':<40} : {time.time()-s:.4f} sec")
    conn.close()

    # Test Trigger
    test_trigger_capacity()

if __name__ == "__main__":
    run_benchmarks()
