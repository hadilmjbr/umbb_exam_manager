from backend.db import get_connection
import pandas as pd
import streamlit as st
import importlib

# =====================================================
# 1. DASHBOARD & KPIs
# =====================================================
def get_dashboard_kpis():
    """
    Recupere les indicateurs globaux depuis la base de données.
    Retourne un dictionnaire avec les valeurs.
    """
    conn = get_connection()
    if not conn:
        return None
    
    stats = {}
    try:
        cur = conn.cursor()
        
        # Requetes pour les KPIs
        queries = {
            "nb_examens": "SELECT COUNT(*) FROM examens",
            "nb_etudiants": "SELECT COUNT(*) FROM etudiants",
            "nb_professeurs": "SELECT COUNT(*) FROM professeurs",
            "nb_salles": "SELECT COUNT(*) FROM salles",
            "nb_departements": "SELECT COUNT(*) FROM departements",
            "nb_formations": "SELECT COUNT(*) FROM formations"
        }
        
        for key, query in queries.items():
            cur.execute(query)
            stats[key] = cur.fetchone()[0]
            
        # Status counts
        cur.execute("SELECT statut, COUNT(*) FROM validation_pedagogique GROUP BY statut")
        statuses = dict(cur.fetchall())
        stats["status_counts"] = statuses

        # Date de generation reelle
        cur.execute("SELECT valeur FROM parametres WHERE cle = 'last_generation'")
        res = cur.fetchone()
        stats["last_generation"] = res[0] if res else "Aucune"
        
        cur.close()
        return stats
    except Exception as e:
        return None
    finally:
        conn.close()

def get_departments():
    conn = get_connection()
    if not conn: return pd.DataFrame()
    df = pd.read_sql("SELECT id, nom FROM departements ORDER BY nom", conn)
    conn.close()
    return df

def get_formations_by_dept(dept_id):
    conn = get_connection()
    if not conn: return pd.DataFrame()
    df = pd.read_sql("SELECT id, nom FROM formations WHERE dept_id = %s ORDER BY nom", conn, params=[dept_id])
    conn.close()
    return df

# =====================================================
# 2. GENERATION LOGIC
# =====================================================
def generate_schedule_heuristic(params):
    """
    Appelle le moteur de generation (backend/generate_examens.py).
    """
    try:
        import backend.generate_examens as engine
        importlib.reload(engine)
        
        date_debut = params.get('date_debut')
        engine.generer_examens(date_debut)
        
        return True, "Generation terminee. Les emplois du temps sont en statut 'BROUILLON'."
    except Exception as e:
        return False, f"Erreur lors de la generation: {e}"

def submit_to_chefs():
    """
    Envoie tous les examens en statut 'BROUILLON' vers 'EN_ATTENTE_CHEF'.
    """
    conn = get_connection()
    if not conn: return False, "Erreur connexion"
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE validation_pedagogique 
            SET statut = 'EN_ATTENTE_CHEF', date_maj = CURRENT_TIMESTAMP
            WHERE statut = 'BROUILLON'
        """)
        conn.commit()
        count = cur.rowcount
        cur.close()
        return True, f"{count} formations transmises aux chefs de departement."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# =====================================================
# 3. PLANNING VIEW
# =====================================================
def get_global_schedule(formation_id=None):
    """
    Recupere le planning complet ou filtre par formation.
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    query = """
        SELECT 
            f.nom as "Formation",
            m.nom as "Module",
            e.date_heure as "Date/Heure",
            e.duree as "Duree (min)",
            s.nom as "Salle",
            p.nom as "Surveillant",
            v.statut as "Statut"
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN salles s ON e.salle_id = s.id
        JOIN professeurs p ON e.prof_id = p.id
        LEFT JOIN validation_pedagogique v ON f.id = v.formation_id
    """
    params = []
    if formation_id:
        query += " WHERE f.id = %s"
        params.append(formation_id)
        
    query += " ORDER BY e.date_heure, f.nom"
    
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# =====================================================
# 4. RESET & UTILS
# =====================================================
def reset_simulation():
    """
    Supprime toutes les donnees generees (examens, validations).
    """
    conn = get_connection()
    if not conn: return False, "Erreur connexion"
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM examens")
        cur.execute("DELETE FROM validation_pedagogique")
        cur.execute("DELETE FROM parametres WHERE cle = 'last_generation'")
        conn.commit()
        cur.close()
        return True, "Simulation reinitialisee."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def audit_quality():
    """
    Appelle les fonctions de verification de contraintes.
    """
    conn = get_connection()
    if not conn: return None
    
    reports = {}
    try:
        # 0. Vendredis (Interdit)
        # 5 = Vendredi dans PostgreSQL (dimanche=0 ... samedi=6 ou depends on lc_time)
        # Plus fiable : extract(dow from date_heure) = 5
        query_fri = """
            SELECT m.nom as module, e.date_heure, f.nom as formation
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE EXTRACT(DOW FROM e.date_heure) = 5
        """
        reports['vendredi'] = pd.read_sql(query_fri, conn)

        # 1. Conflits Etudiants (Meme heure)
        query_etud = """
            SELECT i1.etudiant_id, m1.nom as mod1, m2.nom as mod2, e1.date_heure
            FROM examens e1
            JOIN examens e2 ON e1.date_heure = e2.date_heure AND e1.id < e2.id
            JOIN inscriptions i1 ON e1.module_id = i1.module_id
            JOIN inscriptions i2 ON e2.module_id = i2.module_id AND i1.etudiant_id = i2.etudiant_id
            JOIN modules m1 ON e1.module_id = m1.id
            JOIN modules m2 ON e2.module_id = m2.id
        """
        reports['etudiants'] = pd.read_sql(query_etud, conn)
        
        # 2. Capacite Salles
        query_salles = """
            SELECT s.nom as salle, s.capacite, COUNT(i.etudiant_id) as inscrits, m.nom as module
            FROM examens e
            JOIN salles s ON e.salle_id = s.id
            JOIN modules m ON e.module_id = m.id
            LEFT JOIN inscriptions i ON m.id = i.module_id
            GROUP BY e.id, s.id, m.id
            HAVING COUNT(i.etudiant_id) > s.capacite
        """
        reports['salles'] = pd.read_sql(query_salles, conn)
        
        # 3. Disponibilite Profs
        query_profs = """
            SELECT p.nom, e1.date_heure, m1.nom as mod1, m2.nom as mod2
            FROM examens e1
            JOIN examens e2 ON e1.date_heure = e2.date_heure AND e1.id < e2.id
            JOIN professeurs p ON e1.prof_id = p.id AND e2.prof_id = p.id
            JOIN modules m1 ON e1.module_id = m1.id
            JOIN modules m2 ON e2.module_id = m2.id
        """
        reports['profs'] = pd.read_sql(query_profs, conn)

        # 4. Examens non planifies
        query_non_plan = """
            SELECT m.nom as module, f.nom as formation
            FROM modules m
            JOIN formations f ON m.formation_id = f.id
            WHERE m.id NOT IN (SELECT module_id FROM examens)
        """
        reports['non_planifies'] = pd.read_sql(query_non_plan, conn)

        # 5. Examens sans salle ou sans prof
        query_manquants = """
            SELECT m.nom as module, e.date_heure
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            WHERE e.salle_id IS NULL OR e.prof_id IS NULL
        """
        reports['manquants'] = pd.read_sql(query_manquants, conn)

        return reports
    finally:
        conn.close()
