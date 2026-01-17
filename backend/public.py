from backend.db import get_connection
import pandas as pd

def get_all_professors():
    """Returns a DataFrame of all professors for the searchbox."""
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        return pd.read_sql("SELECT id, nom, dept_id FROM professeurs ORDER BY nom", conn)
    finally:
        conn.close()

def get_professor_details(prof_id):
    """Returns basic details (Name, Dept) of a specific professor."""
    conn = get_connection()
    if not conn: return None
    try:
        query = """
            SELECT p.id, p.nom, d.nom as departement 
            FROM professeurs p
            LEFT JOIN departements d ON p.dept_id = d.id
            WHERE p.id = %s
        """
        df = pd.read_sql(query, conn, params=(int(prof_id),))
        if not df.empty:
            return df.iloc[0]
        return None
    finally:
        conn.close()

def get_professor_exams(prof_id):
    """
    Returns the schedule for a specific professor.
    Joins with modules, formations, salles.
    ONLY returns PUBLISHED schedules.
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        query = """
            SELECT 
                e.id,
                m.nom as module,
                f.nom as formation,
                e.date_heure,
                e.duree,
                s.nom as salle,
                s.type as type_salle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN salles s ON e.salle_id = s.id
            JOIN validation_pedagogique v ON f.id = v.formation_id
            WHERE e.prof_id = %s AND v.statut = 'PUBLIE'
            ORDER BY e.date_heure ASC
        """
        df = pd.read_sql(query, conn, params=(int(prof_id),))
        return df
    finally:
        conn.close()

def get_all_departments():
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        return pd.read_sql("SELECT id, nom FROM departements ORDER BY nom", conn)
    finally:
        conn.close()

def get_formations_by_dept_public(dept_id):
    """ONLY returns formations with PUBLISHED schedules."""
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        query = """
            SELECT f.id, f.nom 
            FROM formations f
            JOIN validation_pedagogique v ON f.id = v.formation_id
            WHERE f.dept_id = %s AND v.statut = 'PUBLIE'
            ORDER BY f.nom
        """
        return pd.read_sql(query, conn, params=(int(dept_id),))
    finally:
        conn.close()

def get_formation_exams_public(formation_id):
    """ONLY returns exams for standard Public view IF published."""
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        query = """
            SELECT 
                m.nom as module,
                e.date_heure,
                e.duree,
                s.nom as salle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN salles s ON e.salle_id = s.id
            JOIN validation_pedagogique v ON m.formation_id = v.formation_id
            WHERE m.formation_id = %s AND v.statut = 'PUBLIE'
            ORDER BY e.date_heure ASC
        """
        return pd.read_sql(query, conn, params=(int(formation_id),))
    finally:
        conn.close()
