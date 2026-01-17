from backend.db import get_connection
import pandas as pd
import numpy as np

def get_global_kpis():
    conn = get_connection()
    if not conn: return {}
    try:
        kpis = {}
        # Simple counts
        kpis['nb_examens'] = pd.read_sql("SELECT COUNT(*) FROM examens", conn).iloc[0, 0]
        kpis['nb_etudiants'] = pd.read_sql("SELECT COUNT(*) FROM etudiants", conn).iloc[0, 0]
        kpis['nb_profs'] = pd.read_sql("SELECT COUNT(DISTINCT prof_id) FROM examens WHERE prof_id IS NOT NULL", conn).iloc[0, 0]
        kpis['nb_salles'] = pd.read_sql("SELECT COUNT(DISTINCT salle_id) FROM examens WHERE salle_id IS NOT NULL", conn).iloc[0, 0]
        
        # Days duration
        dates = pd.read_sql("SELECT MIN(date_heure) as start, MAX(date_heure) as end FROM examens", conn)
        if not dates.empty and dates.iloc[0]['start']:
            start = dates.iloc[0]['start']
            end = dates.iloc[0]['end']
            kpis['duree_jours'] = (end - start).days + 1
        else:
            kpis['duree_jours'] = 0
            
        return kpis
    finally:
        conn.close()

def get_exams_by_dept():
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        query = """
            SELECT d.nom as departement, COUNT(e.id) as nb_examens
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.dept_id = d.id
            GROUP BY d.nom
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_exams_by_level():
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        # We need to parse level from formation name (e.g. "L3 Informatique" -> "L3")
        # Since SQL parsing might be complex depending on DB, we'll fetch and process in pandas
        query = """
            SELECT f.nom as formation, COUNT(e.id) as nb_examens
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            GROUP BY f.nom
        """
        df = pd.read_sql(query, conn)
        
        def extract_level(name):
            parts = name.split()
            if parts:
                first = parts[0].upper()
                if first in ['L1', 'L2', 'L3', 'M1', 'M2']:
                    return first
            return "Autre"
            
        if not df.empty:
            df['Niveau'] = df['formation'].apply(extract_level)
            return df.groupby('Niveau')['nb_examens'].sum().reset_index()
        return pd.DataFrame(columns=['Niveau', 'nb_examens'])
    finally:
        conn.close()

def get_prof_load_stats():
    conn = get_connection()
    if not conn: return pd.DataFrame(), pd.DataFrame()
    try:
        query = """
            SELECT p.nom, COUNT(e.id) as nb_surveillances
            FROM professeurs p
            LEFT JOIN examens e ON p.id = e.prof_id
            GROUP BY p.id, p.nom
        """
        df = pd.read_sql(query, conn)
        
        # Categorization
        conditions = [
            (df['nb_surveillances'] <= 2),
            (df['nb_surveillances'] > 2) & (df['nb_surveillances'] <= 5),
            (df['nb_surveillances'] > 5)
        ]
        choices = ['Faible (0-2)', 'Moyenne (3-5)', 'Élevée (>5)']
        df['Charge'] = np.select(conditions, choices, default='Faible (0-2)')
        
        distrib = df['Charge'].value_counts().reset_index()
        distrib.columns = ['Categorie', 'Nombre']
        
        return df, distrib
    finally:
        conn.close()

def get_student_stats():
    conn = get_connection()
    if not conn: return pd.DataFrame(), pd.DataFrame()
    try:
        # Students per formation
        q1 = """
            SELECT f.nom as formation, COUNT(et.id) as nb_etudiants
            FROM formations f
            LEFT JOIN etudiants et ON f.id = et.formation_id
            GROUP BY f.nom
        """
        df_students = pd.read_sql(q1, conn)
        
        # Exams per day
        q2 = """
            SELECT DATE(date_heure) as jour, COUNT(*) as nb_examens
            FROM examens
            GROUP BY DATE(date_heure)
            ORDER BY jour
        """
        df_days = pd.read_sql(q2, conn)
        
        return df_students, df_days
    finally:
        conn.close()

def get_room_stats():
    conn = get_connection()
    if not conn: return pd.DataFrame(), pd.DataFrame()
    try:
        # Occupancy (Simplified: Just showing capacity vs simple average usage is hard without slots, 
        # so we'll show Usage Count per Room)
        q1 = """
            SELECT s.nom, s.type, s.capacite, COUNT(e.id) as nb_ulisations
            FROM salles s
            LEFT JOIN examens e ON s.id = e.salle_id
            GROUP BY s.id, s.nom, s.type, s.capacite
        """
        df_rooms = pd.read_sql(q1, conn)
        
        # Type distribution
        df_types = df_rooms['type'].value_counts().reset_index()
        df_types.columns = ['Type', 'Nombre']
        
        return df_rooms, df_types
    finally:
        conn.close()

def get_compliance_metrics():
    # Reuse logic from verify_audit or similar, but simplified for display
    # We'll valid Fridays and Conflicts (Student overlap)
    conn = get_connection()
    if not conn: return {}
    
    metrics = {
        'conflits': 0,
        'examens_ok': 0,
        'conformite': 100
    }
    
    try:
        # Check Fridays
        fri = pd.read_sql("SELECT COUNT(*) FROM examens WHERE EXTRACT(ISODOW FROM date_heure) = 5", conn).iloc[0,0]
        
        # Check Student Conflicts (Simplified: same slot same formation)
        # Note: True student conflict check is heavier, well use Module overlap within formation as proxy for quick dashboard
        # Actually let's just count total exams and assume audit was run separately. 
        # Or better, run a lightweight overlap check: same formation, same time.
        q_conf = """
            SELECT COUNT(*) 
            FROM examens e1
            JOIN examens e2 ON e1.id < e2.id 
            JOIN modules m1 ON e1.module_id = m1.id
            JOIN modules m2 ON e2.module_id = m2.id
            WHERE m1.formation_id = m2.formation_id
            AND e1.date_heure < (e2.date_heure + (e2.duree * INTERVAL '1 minute'))
            AND e2.date_heure < (e1.date_heure + (e1.duree * INTERVAL '1 minute'))
        """
        conflicts = pd.read_sql(q_conf, conn).iloc[0, 0]
        
        total = pd.read_sql("SELECT COUNT(*) FROM examens", conn).iloc[0, 0]
        
        metrics['conflits'] = conflicts
        metrics['examens_ok'] = total - conflicts
        if total > 0:
            metrics['conformite'] = round(((total - conflicts) / total) * 100, 1)
            
        return metrics
    finally:
        conn.close()
