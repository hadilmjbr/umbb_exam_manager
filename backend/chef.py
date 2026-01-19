import pandas as pd
from backend.db import get_connection

def get_department_kpis(dept_id):
    """Calcule les stats globales pour le departement."""
    conn = get_connection()
    if not conn: return {}
    
    stats = {"exams": 0, "students": 0, "profs": 0}
    try:
        cur = conn.cursor()
        
        # 1. Nombre d'examens (lies aux formations du dept)
        # examens -> modules -> formations -> dept_id
        q_exams = """
            SELECT COUNT(e.id)
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.dept_id = %s
        """
        cur.execute(q_exams, (dept_id,))
        stats["exams"] = cur.fetchone()[0]
        
        # 2. Nombre d'etudiants (Inscrits dans des modules du dept)
        # inscriptions -> modules -> formations -> dept_id
        q_students = """
            SELECT COUNT(DISTINCT i.etudiant_id)
            FROM inscriptions i
            JOIN modules m ON i.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.dept_id = %s
        """
        cur.execute(q_students, (dept_id,))
        stats["students"] = cur.fetchone()[0]
        
        # 3. Nombre de professeurs (Rattaches au dept)
        # professeurs -> dept_id
        q_profs = "SELECT COUNT(*) FROM professeurs WHERE dept_id = %s"
        cur.execute(q_profs, (dept_id,))
        stats["profs"] = cur.fetchone()[0]
        
        cur.close()
    except:
        pass
    finally:
        conn.close()
    return stats

def get_dept_formations_with_status(dept_id):
    """
    Recupere les formations du departement qui SONT dans le processus de validation.
    Effectue une jointure pour ne garder que celles que l'Admin a envoyees.
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    query = """
        SELECT f.id, f.nom, v.statut, v.commentaire, v.date_maj
        FROM formations f
        LEFT JOIN validation_pedagogique v ON f.id = v.formation_id
        WHERE f.dept_id = %s
        ORDER BY f.nom
    """
    df = pd.read_sql(query, conn, params=[dept_id])
    conn.close()
    return df

def get_formations_by_dept(dept_id):
    """Recupere les formations d'un departement."""
    conn = get_connection()
    if not conn: return pd.DataFrame()
    query = "SELECT id, nom FROM formations WHERE dept_id = %s ORDER BY nom"
    df = pd.read_sql(query, conn, params=[dept_id])
    conn.close()
    return df

def get_department_schedule(dept_id):
    """Recupere tout le planning d'un departement avec les noms."""
    conn = get_connection()
    if not conn: return pd.DataFrame()
    query = """
        SELECT f.nom as formation, m.nom as module, e.date_heure, s.nom as salle, p.nom as surveillant, v.statut
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN salles s ON e.salle_id = s.id
        JOIN professeurs p ON e.prof_id = p.id
        JOIN validation_pedagogique v ON f.id = v.formation_id
        WHERE f.dept_id = %s
        ORDER BY f.nom, e.date_heure
    """
    df = pd.read_sql(query, conn, params=[dept_id])
    conn.close()
    return df

def submit_validation(formation_id, statut, commentaire):
    """Enregistre ou met a jour la validation d'une formation (Chef ou Doyen)."""
    if "REFUSE" in statut and (not commentaire or len(commentaire.strip()) < 5):
        return False, "Un commentaire explicatif est obligatoire en cas de refus."
        
    conn = get_connection()
    if not conn: return False, "Erreur connexion"
    try:
        cur = conn.cursor()
        
        # Mappage des statuts pour la publication finale
        # Si le Doyen valide -> statut = 'PUBLIE'
        final_statut = 'PUBLIE' if statut == 'VALIDE_DOYEN' else statut
        
        cur.execute("""
            INSERT INTO validation_pedagogique (formation_id, statut, commentaire, date_maj)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (formation_id) DO UPDATE 
            SET statut = EXCLUDED.statut, commentaire = EXCLUDED.commentaire, date_maj = CURRENT_TIMESTAMP
        """, (formation_id, final_statut, commentaire))
        conn.commit()
        cur.close()
        return True, "Validation enregistree avec succes."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_validation_history(dept_id):
    """Recupere l'historique des validations du departement."""
    conn = get_connection()
    if not conn: return pd.DataFrame()
    query = """
        SELECT f.nom as formation, v.statut, v.commentaire, v.date_maj
        FROM validation_pedagogique v
        JOIN formations f ON v.formation_id = f.id
        WHERE f.dept_id = %s
        ORDER BY v.date_maj DESC
    """
    df = pd.read_sql(query, conn, params=[dept_id])
    conn.close()
    return df

def get_formation_exams_details(formation_id):
    """
    Recupere les details des examens pour une formation specifique
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    query = """
        SELECT 
            m.nom as "Module",
            e.date_heure::date as "Date",
            TO_CHAR(e.date_heure, 'HH24:MI') || ' - ' || TO_CHAR(e.date_heure + interval '90 minutes', 'HH24:MI') as "Horaire (1h30)",
            s.nom as "Salle",
            s.capacite as "Capacite Salle",
            p.nom as "Surveillant",
            (SELECT COUNT(*) FROM inscriptions i WHERE i.module_id = m.id) as "Nb Etudiants"
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN salles s ON e.salle_id = s.id
        JOIN professeurs p ON e.prof_id = p.id
        WHERE m.formation_id = %s
        ORDER BY e.date_heure
    """
    df = pd.read_sql(query, conn, params=[formation_id])
    conn.close()
    return df

def get_doyen_dashboard_stats():
    """
    Retourne un resume par departement pour le Doyen
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    query = """
        SELECT 
            d.id,
            d.nom as "Département",
            COUNT(f.id) as "Total Formations",
            SUM(CASE WHEN v.statut = 'VALIDE_CHEF' THEN 1 ELSE 0 END) as "En Attente Doyen",
            SUM(CASE WHEN v.statut = 'PUBLIE' THEN 1 ELSE 0 END) as "Publiés"
        FROM departements d
        LEFT JOIN formations f ON d.id = f.dept_id
        LEFT JOIN validation_pedagogique v ON f.id = v.formation_id
        GROUP BY d.id, d.nom
        ORDER BY d.nom
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_doyen_pending_validations(dept_id):
    """
    Recupere les formations d'un departement pretes pour le Doyen (VALIDE_CHEF) ou deja traitees.
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    query = """
        SELECT f.id, f.nom, v.statut, v.date_maj, v.commentaire
        FROM formations f
        JOIN validation_pedagogique v ON f.id = v.formation_id
        WHERE f.dept_id = %s AND (v.statut = 'VALIDE_CHEF' OR v.statut = 'PUBLIE' OR v.statut = 'REFUSE_DOYEN')
        ORDER BY f.nom
    """
    df = pd.read_sql(query, conn, params=[dept_id])
    conn.close()
    return df

def get_department_audit(dept_id):
    """Version filtree de l'audit pour un departement specifique."""
    conn = get_connection()
    if not conn: return {}
    
    reports = {}
    try:
        # 1. Etudiants (Conflits filtres)
        query_etudiants = """
            SELECT i1.etudiant_id, m1.nom as module1, m2.nom as module2, e1.date_heure
            FROM examens e1
            JOIN examens e2 ON e1.date_heure = e2.date_heure AND e1.id < e2.id
            JOIN inscriptions i1 ON e1.module_id = i1.module_id
            JOIN inscriptions i2 ON e2.module_id = i2.module_id AND i1.etudiant_id = i2.etudiant_id
            JOIN modules m1 ON e1.module_id = m1.id
            JOIN modules m2 ON e2.module_id = m2.id
            JOIN formations f1 ON m1.formation_id = f1.id
            WHERE f1.dept_id = %s
        """
        reports['etudiants'] = pd.read_sql(query_etudiants, conn, params=[dept_id])

        # 2. Salles (Capacite filtree)
        query_salles = """
            SELECT s.nom as salle, s.capacite, COUNT(i.etudiant_id) as inscrits, m.nom as module
            FROM examens e
            JOIN salles s ON e.salle_id = s.id
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            LEFT JOIN inscriptions i ON m.id = i.module_id
            WHERE f.dept_id = %s
            GROUP BY e.id, s.id, m.id
            HAVING COUNT(i.etudiant_id) > s.capacite
        """
        reports['salles'] = pd.read_sql(query_salles, conn, params=[dept_id])
    finally:
        conn.close()
    return reports

def get_doyen_validations():
    """
    Recupere les formations a valider par le Doyen (Statut: VALIDE_CHEF) ou deja traitees.
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    query = """
        SELECT f.id, f.nom as formation, d.nom as departement, v.statut, v.commentaire, v.date_maj
        FROM validation_pedagogique v
        JOIN formations f ON v.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        WHERE v.statut IN ('VALIDE_CHEF', 'PUBLIE', 'REFUSE_DOYEN')
        ORDER BY d.nom, f.nom
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
