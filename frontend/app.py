import sys
import os
import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =====================================================
# 1. SETUP & CONNEXION BDD
# =====================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from backend.db import get_connection
except ImportError:
    st.error(" Erreur : Impossible de charger le backend.")
    st.stop()

# --- CSS Injection for Professional UI (University Theme) ---
st.markdown("""
<style>
/* 1. Global Reset & Fonts */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Roboto', 'Segoe UI', sans-serif;
    color: #333333;
}

/* 2. Main Background (Light Blue neutral) */
.stApp {
    background-color: #F4F7F6;
}

/* 3. Headers */
h1, h2, h3 {
    color: #0D47A1; /* Dark Blue */
    font-weight: 600;
}
h1 { font-size: 2.2rem; }
h2 { font-size: 1.8rem; border-bottom: 2px solid #E0E0E0; padding-bottom: 10px; margin-bottom: 20px; }
h3 { font-size: 1.4rem; color: #1565C0; }

/* 4. Buttons (Bootstrap-like) - ALL DARK BLUE AS REQUESTED */
/* General Button */
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    border-radius: 6px;
    height: 3em;
    font-weight: 500;
    border: none;
    transition: all 0.2s ease-in-out;
    background-color: #0D47A1 !important; /* Force Dark Blue */
    color: white !important;
}

div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #082E6E !important; /* Darker Blue */
    color: white !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

div.stButton > button:focus, div[data-testid="stFormSubmitButton"] > button:focus {
    box-shadow: none;
    color: white !important;
}

/* Primary Button Override - Ensure it's not Red */
div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background-color: #0D47A1 !important;
    color: white !important;
    border: none;
}

/* 5. Metrics styling */
div[data-testid="stMetricValue"] {
    font-size: 2rem;
    color: #0D47A1;
    font-weight: 700;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.9rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* 6. Card-like Containers */
div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* 7. Tables */
div[data-testid="stDataFrame"] {
    border: 1px solid #E0E0E0;
    border-radius: 5px;
    overflow: hidden;
}
thead tr th {
    background-color: #E3F2FD !important;
    color: #0D47A1 !important;
    font-weight: bold !important;
}
tbody tr:nth-child(even) {
    background-color: #F9F9F9;
}

/* 8. Alerts */
div.stAlert {
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Load Public Backend
import backend.public as public_backend
try:
    import backend.pdf_gen as pdf_gen
except ImportError:
    pdf_gen = None
    print("Warning: reportlab not found. PDF generation will be disabled.")

def load_data(query):
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erreur SQL : {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def render_user_header():
    """
    Affiche le header utilisateur en haut de la page avec:
    - Nom de l'utilisateur
    - Son rôle  
    - Bouton de déconnexion
    """
    if 'user' not in st.session_state or not st.session_state.user:
        return
    
    user = st.session_state.user
    
    with st.container():
        # Clean Header (No Background Box)
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            role_display = {
                'ADMIN': 'Administrateur',
                'DOYEN': 'Doyen',
                'CHEF': 'Chef de Département',
                'PROF': 'Professeur',
                'ETUDIANT': 'Étudiant'
            }
            # Styled User Info (Dark Blue Text)
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px;">
                <h3 style="margin: 0; color: #0D47A1;">{user.get('username', 'Utilisateur')}</h3>
                <span style="background-color: #E3F2FD; color: #0D47A1; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: bold;">
                    {role_display.get(user['role'], user['role'])}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_right:
            # Using secondary button for logout which is now Dark Blue too
            if st.button("Déconnexion", key="logout_btn", type="secondary", use_container_width=True):
                st.session_state.user = None
                st.rerun()
                
        st.divider()


# =====================================================
# 2. INTERFACES PAR ACTEUR
# =====================================================

# --- A. INTERFACE DOYEN (Vue Stratégique) ---
# --- A. INTERFACE DOYEN (Vue Stratégique) ---
def interface_doyen():
    render_user_header()
    
    import backend.chef as schema_backend
    import backend.doyen_dashboard as doyen_dash
    import importlib
    importlib.reload(schema_backend)
    importlib.reload(doyen_dash)

    st.title("Espace Doyen : Supervision & Validation")
    
    tab_dash, tab_valid = st.tabs(["Vue Stratégique", "Validation & Publication"])

    # --- TAB 1: DASHBOARD STRATEGIQUE ---
    with tab_dash:
        st.header("Tableau de Bord Stratégique")
        
        # 1. KPIs
        kpis = doyen_dash.get_global_kpis()
        if kpis:
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Examens", kpis.get('nb_examens', 0))
            k2.metric("Étudiants", kpis.get('nb_etudiants', 0))
            k3.metric("Professeurs", kpis.get('nb_profs', 0))
            k4.metric("Salles", kpis.get('nb_salles', 0))
            k5.metric("Durée (Jours)", kpis.get('duree_jours', 0))
        
        st.divider()
        
        # 2. Charts Row 1: Exams
        c_dept, c_level = st.columns(2)
        with c_dept:
            st.subheader("Examens par Département")
            df_dept = doyen_dash.get_exams_by_dept()
            if not df_dept.empty:
                st.bar_chart(df_dept.set_index('departement'))
            else: st.info("Pas de données.")
            
        with c_level:
            st.subheader("Examens par Niveau")
            df_level = doyen_dash.get_exams_by_level()
            if not df_level.empty:
                fig = px.pie(df_level, values='nb_examens', names='Niveau', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Pas de données.")

        st.divider()

        # 3. Charts Row 2: Profs
        c_load, c_dist = st.columns(2)
        with c_load:
            st.subheader("Charge Professeurs")
            df_prof, df_cat = doyen_dash.get_prof_load_stats()
            if not df_prof.empty:
                # Top 10 busiest
                top_profs = df_prof.sort_values('nb_surveillances', ascending=False).head(10)
                st.bar_chart(top_profs.set_index('nom')['nb_surveillances'])
            else: st.info("Pas de données.")
            
        with c_dist:
            st.subheader("Répartition de la Charge")
            if 'df_cat' in locals() and not df_cat.empty:
                fig2 = px.pie(df_cat, values='Nombre', names='Categorie', color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # 4. Charts Row 3: Students & Rooms
        c_stud, c_room = st.columns(2)
        with c_stud:
            st.subheader("Examens par Jour")
            _, df_days = doyen_dash.get_student_stats()
            if not df_days.empty:
                st.area_chart(df_days.set_index('jour'))
            else: st.info("Pas de données.")
            
        with c_room:
            st.subheader("Salles vs Amphis")
            _, df_types = doyen_dash.get_room_stats()
            if not df_types.empty:
                fig3 = px.pie(df_types, values='Nombre', names='Type')
                st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # 5. Compliance
        st.subheader("Qualité & Conformité")
        comp = doyen_dash.get_compliance_metrics()
        q1, q2, q3 = st.columns(3)
        q1.metric("Conflits Détectés", comp.get('conflits', 0), delta_color="inverse")
        q2.metric("Examens Sans Conflit", comp.get('examens_ok', 0))
        q3.metric("Taux de Conformité", f"{comp.get('conformite', 0)}%")


    # --- TAB 2: VALIDATION (Code Existant préservé) ---
    with tab_valid:
        st.header("Validation Administrative")
    
        # 1. Dashboard Départements
        st.subheader("État des Départements")
    
        stats_depts = schema_backend.get_doyen_dashboard_stats()
        
        if not stats_depts.empty:
            # Affichage en grid
            cols = st.columns(3)
            for i, row in stats_depts.iterrows():
                col = cols[i % 3]
                with col:
                    with st.container(border=True):
                        st.markdown(f"#### {row['Département']}")
                        
                        # Status Indicator
                        pending = int(row['En Attente Doyen'] or 0)
                        published = int(row['Publiés'] or 0)
                        
                        if pending > 0:
                            st.warning(f"En attente: {pending}")
                        elif published > 0:
                            st.success("À jour")
                        else:
                            st.info("Rien à signaler")
                            
                        if st.button(f"Gérer {row['Département']}", key=f"dept_btn_{row['id']}"):
                            st.session_state['doyen_selected_dept'] = row['id']
                            st.session_state['doyen_selected_dept_name'] = row['Département']
                            st.rerun()
        
        st.divider()

        # 2. Vue Détail Département (si sélectionné)
        if 'doyen_selected_dept' in st.session_state:
            dept_id = st.session_state['doyen_selected_dept']
            dept_name = st.session_state['doyen_selected_dept_name']
            
            st.markdown(f"## Département : {dept_name}")
            if st.button("Retour à la liste"):
                del st.session_state['doyen_selected_dept']
                st.rerun()
                
            formations = schema_backend.get_doyen_pending_validations(dept_id)
            
            if not formations.empty:
                for _, fmt in formations.iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        c1.markdown(f"### {fmt['nom']}")
                        if fmt['statut'] == 'PUBLIE':
                            c2.success("PUBLIÉ OFFICIELLEMENT")
                        else:
                            c2.info("En attente de publication")
                        
                        # Consultation READ-ONLY
                        with st.expander("Consulter l'EDT (Lecture Seule)"):
                            details = schema_backend.get_formation_exams_details(fmt['id'])
                            if not details.empty:
                                st.table(details)
                            else:
                                st.warning("EDT vide.")

                        # Actions (Uniquement si pas encore publié)
                        if fmt['statut'] == 'VALIDE_CHEF':
                            st.write("---")
                            c_act1, c_act2 = st.columns(2)
                            
                            with c_act1:
                                st.markdown("##### Validation Finale")
                                st.caption("L'EDT deviendra visible pour tous les étudiants et professeurs. Action irréversible.")
                                if st.button("Valider & Publier", key=f"pub_{fmt['id']}", type="primary", use_container_width=True):
                                    s, m = schema_backend.submit_validation(fmt['id'], "VALIDE_DOYEN", "Valide par le Doyen")
                                    if s: 
                                        st.success("Publie avec succes !")
                                        time.sleep(1)
                                        st.rerun()
                                    else: st.error(m)
                                    
                            with c_act2:
                                st.markdown("##### Refus Exceptionnel")
                                st.caption("Renvoie le dossier au Chef de Département pour correction.")
                                if st.toggle("Refuser l'EDT", key=f"tog_ref_doy_{fmt['id']}"):
                                    reason = st.text_area("Motif du refus (Obligatoire)", key=f"reas_doy_{fmt['id']}")
                                    if st.button("Retour au Département", key=f"ret_doy_{fmt['id']}", type="secondary"):
                                        if not reason.strip():
                                            st.error("Motif requis.")
                                        else:
                                            s, m = schema_backend.submit_validation(fmt['id'], "REFUSE_DOYEN", reason)
                                            if s: st.error("Renvoyé au département !"); time.sleep(1); st.rerun()
                                            else: st.error(m)
            else:
                 st.info("Aucune formation validée par le département pour le moment.")

# --- B. INTERFACE ADMIN (Génération & Algo) ---
def interface_admin():
    render_user_header()
    
    import backend.admin as admin_backend
    import backend.admin_workflow as admin_wf
    import backend.generate_examens as gen_exo
    import importlib
    import time
    importlib.reload(admin_backend)
    importlib.reload(gen_exo)
    importlib.reload(admin_wf)

    conn_status = "Connecté" if admin_backend.get_connection() else "Déconnecté"
    st.sidebar.info(f"État BDD: {conn_status}")

    tab1, tab2, tab3, tab4 = st.tabs(["Tableau de Bord", "Générateur", "Planning Global", "Audit & Qualité"])
    
    # 1. Tableau de bord (Dashboard Admin)
    with tab1:
        st.header("Tableau de Bord Administrateur")
        
        c_dash1, c_dash2 = st.columns([3, 1])
        with c_dash1:
            if st.button("Actualiser les données"):
                st.rerun()
        with c_dash2:
             # Reset Button with Confirmation
             if st.button("Réinitialiser tout", type="primary", use_container_width=True):
                 with st.spinner("Réinitialisation en cours..."):
                     ok, msg = admin_backend.reset_simulation()
                     if ok: st.success("Réinitialisation terminée !"); time.sleep(1); st.rerun()
                     else: st.error(msg)

        stats = admin_backend.get_dashboard_kpis()
        
        if stats:
            col1, col2, col3 = st.columns(3)
            col1.metric("Examens", stats['nb_examens'])
            col2.metric("Étudiants", stats['nb_etudiants'])
            col3.metric("Professeurs", stats['nb_professeurs'])
            
            col4, col5, col6 = st.columns(3)
            col4.metric("Salles", stats['nb_salles'])
            col5.metric("Formations", stats['nb_formations'])
            col6.metric("Départements", stats['nb_departements'])
            
            st.caption(f"Dernière mise à jour du planning (Date max examen) : {stats['last_generation']}")
            
            st.divider()
            st.subheader("Suivi des Validations")
            
            # KPI States overview
            sc = stats.get('status_counts', {})
            c1, c2, c3, c4 = st.columns(4)
            c1.info(f"Brouillon: {sc.get('BROUILLON', 0)}")
            c2.warning(f"Attente Chef/Doyen: {sc.get('EN_ATTENTE_CHEF', 0) + sc.get('VALIDE_CHEF', 0)}")
            c3.error(f"Refusés: {sc.get('REFUSE_CHEF', 0) + sc.get('REFUSE_DOYEN', 0)}")
            c4.success(f"Publiés: {sc.get('PUBLIE', 0)}")
            
            # --- SECTION RÉSOLUTION DES REFUS ---
            st.divider()
            st.markdown("### Résolution des Refus")
            refus_data = load_data("""
                SELECT f.id, f.nom as formation, v.statut, v.commentaire, v.date_maj
                FROM validation_pedagogique v
                JOIN formations f ON v.formation_id = f.id
                WHERE v.statut LIKE 'REFUSE%'
            """)
            
            if not refus_data.empty:
                for _, row in refus_data.iterrows():
                    with st.container(border=True):
                        col_text, col_btn = st.columns([3, 1])
                        with col_text:
                            st.error(f"**{row['formation']}** ({row['statut']})")
                            st.write(f"Motif : {row['commentaire'] or 'Aucun motif'}")
                        with col_btn:
                            if st.button("Régénérer", key=f"regen_{row['id']}", use_container_width=True):
                                with st.spinner("Régénération..."):
                                    ok, msg = admin_wf.regenerate_formation_schedule(row['id'])
                                    if ok: 
                                        st.success(msg)
                                        time.sleep(1)
                                        st.rerun()
                                    else: st.error(msg)
            else:
                st.info("Aucun refus à traiter actuellement.")

            st.markdown("### Historique Complet & Commentaires")
            retours = load_data("""
                SELECT f.nom as formation, v.statut, v.commentaire, v.date_maj
                FROM validation_pedagogique v
                JOIN formations f ON v.formation_id = f.id
                ORDER BY (CASE WHEN v.statut LIKE 'REFUSE%' THEN 1 WHEN v.statut = 'PUBLIE' THEN 3 ELSE 2 END), v.date_maj DESC
            """)
            
            if not retours.empty:
                st.dataframe(retours, use_container_width=True)
            else:
                st.info("Aucun processus de validation actif.")
        else:
            st.warning("Impossible de récupérer les données.")

    # 2. Générateur automatique
    with tab2:
        st.subheader("Génération Automatique")
        
        col_gen, col_exp = st.columns([2, 3])
        with col_gen:
            st.markdown("#### Paramètres")
            d_start = st.date_input("Date début des examens", datetime(2026, 6, 1))
            
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                if st.button("Lancer Génération", type="primary", use_container_width=True):
                    with st.spinner("Algorithme intelligent en cours..."):
                        params = {"date_debut": d_start}
                        success, msg = admin_backend.generate_schedule_heuristic(params)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            with c_g2:
                if st.button("Soumettre aux Chefs", use_container_width=True):
                    result, msg = admin_backend.submit_to_chefs()
                    if result:
                         st.success(msg)
                         st.info("Transmis pour validation.")
                    else:
                         st.error(msg)

        st.markdown("### Résultats")
        df_schedule = admin_backend.get_global_schedule()
        if not df_schedule.empty:
            st.dataframe(df_schedule, use_container_width=True)
            
            # Export
            csv = df_schedule.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Exporter en CSV",
                data=csv,
                file_name='emploi_du_temps.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucun emploi du temps généré pour le moment.")


    # 3. Planning Global (Granulaire)
    with tab3:
        st.subheader("Planning par Formation")
        
        # Sélecteurs en cascade
        col_dept, col_fmt = st.columns(2)
        
        with col_dept:
            depts = admin_backend.get_departments()
            if not depts.empty:
                selected_dept_id = st.selectbox("Choisir un Département", depts['id'], format_func=lambda x: depts[depts['id'] == x]['nom'].values[0])
            else:
                selected_dept_id = None
        
        with col_fmt:
            selected_fmt_name = "formation"
            if selected_dept_id:
                fmts = admin_backend.get_formations_by_dept(selected_dept_id)
                if not fmts.empty:
                    selected_fmt_id = st.selectbox("Choisir une Formation", fmts['id'], format_func=lambda x: fmts[fmts['id'] == x]['nom'].values[0])
                    # Retrieve Name
                    if selected_fmt_id:
                        selected_fmt_name = fmts[fmts['id'] == selected_fmt_id]['nom'].values[0]
                else:
                    selected_fmt_id = None, st.warning("Aucune formation")
            else:
                selected_fmt_id = None
        
        st.divider()

        if selected_fmt_id:
            df_schedule = admin_backend.get_global_schedule(selected_fmt_id)
            if not df_schedule.empty:
                st.dataframe(df_schedule, use_container_width=True)
                
                # Actions
                c_down, _ = st.columns(2)
                with c_down:
                    # Export spécifique
                    csv = df_schedule.to_csv(index=False).encode('utf-8')
                    file_name_clean = selected_fmt_name.replace(" ", "_")
                    st.download_button(
                        label=f"Télécharger EDT (CSV)",
                        data=csv,
                        file_name=f'emploi_du_temps_{file_name_clean}.csv',
                        mime='text/csv',
                    )
            else:
                st.info("Aucun examen planifié pour cette formation.")
        else:
            st.info("Veuillez sélectionner un département et une formation.")

    # 4. Audit & Qualite
    with tab4:
        st.header("Audit & Qualité")
        
        if st.button("Lancer l'audit de conformité"):
            reports = admin_backend.audit_quality()
            
            if reports:
                # 0. Vendredis
                if 'vendredi' in reports and not reports['vendredi'].empty:
                     st.error(f"{len(reports['vendredi'])} Examens programmés un Vendredi (INTERDIT)")
                     st.dataframe(reports['vendredi'])
                else:
                    st.success("Aucun examen le vendredi.")
                
                # 1. Étudiants
                st.subheader("1. Conflits Étudiants")
                if not reports['etudiants'].empty:
                    st.error(f"{len(reports['etudiants'])} conflits détectés (Étudiants convoqués à plusieurs examens simultanés)")
                    st.dataframe(reports['etudiants'])
                else:
                    st.success("Aucun conflit étudiant détecté.")

                st.markdown("---")

                # 2. Salles
                st.subheader("2. Capacité des Salles")
                if not reports['salles'].empty:
                    st.error(f"{len(reports['salles'])} problèmes de capacité détectés (Plus d'étudiants que de places)")
                    st.dataframe(reports['salles'])
                else:
                    st.success("Capacité des salles conforme.")

                st.markdown("---")

                # 3. Professeurs
                st.subheader("3. Disponibilité des Professeurs")
                if not reports['profs'].empty:
                    st.error(f"{len(reports['profs'])} conflits professeurs détectés")
                    st.dataframe(reports['profs'])
                else:
                    st.success("Planning professeurs valide.")

                # 4. Ressources Manquantes
                st.subheader("4. Complétude des Ressources")
                if 'manquants' in reports and not reports['manquants'].empty:
                    st.error(f"{len(reports['manquants'])} Examens sans salle ou prof assigné !")
                else:
                    st.success("Tous les examens ont une salle et un surveillant.")
            else:
                st.warning("Impossible de lancer l'audit.")
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Corriger automatiquement les conflits"):
                 with st.spinner("Correction en cours (Régénération)..."):
                    # On relance la génération avec la date par défaut ou celle en session si on l'avait stockée
                    # Pour simplifier, on prend une date par défaut futuriste ou on demande à l'user
                    params = {"date_debut": datetime(2026, 6, 1)}
                    success, msg = admin_backend.generate_schedule_heuristic(params)
                    if success: st.success("Correction terminée !"); st.rerun()
                    else: st.error(msg)
        with c2:
            st.write("")

# --- C. INTERFACE CHEF DE DEPARTEMENT (Validation Pédagogique) ---
def interface_chef_dept(dept_id):
    render_user_header()
    
    import backend.chef as chef_backend
    import importlib
    importlib.reload(chef_backend)

    # 1. Identification
    depts = load_data(f"SELECT nom FROM departements WHERE id = {dept_id}")
    if not depts.empty:
        dept_name = depts.iloc[0]['nom']
    else:
        st.error("Département introuvable.")
        return

    st.title(f"Espace Chef de Département : {dept_name}")
    
    selected_dept_id = dept_id # Force usage of logged user's dept

    # --- KPI Cards ---
    st.markdown("### Statistiques")
    stats = chef_backend.get_department_kpis(selected_dept_id)
    k1, k2, k3 = st.columns(3)
    k1.metric("Nombre d'Examens", stats.get('exams', 0))
    k2.metric("Étudiants Concernés", stats.get('students', 0))
    k3.metric("Professeurs Mobilisés", stats.get('profs', 0))
    
    st.divider()

    tab_val, tab_audit, tab_hist = st.tabs(["Liste des Formations & Validation", "Alertes & Audit", "Historique"])

    # --- 1. Liste & Validation ---
    with tab_val:
        st.subheader(f"Formations rattachées à {dept_name}")
        
        formations = chef_backend.get_dept_formations_with_status(selected_dept_id)
        
        if not formations.empty:
            for _, row in formations.iterrows():
                fmt_id = row['id']
                fmt_nom = row['nom']
                statut = row['statut']
                date_maj = row['date_maj']
                
                # --- Badge Statut ---
                status_color = "gray"
                status_text = "En attente de generation"
                
                if statut == 'BROUILLON':
                    status_color = "gray"
                    status_text = "Brouillon (En attente d'envoi)"
                elif statut == 'EN_ATTENTE_CHEF':
                    status_color = "orange"
                    status_text = "En attente de validation"
                elif statut == 'VALIDE_CHEF':
                    status_color = "green"
                    status_text = "Validé par le département"
                elif statut == 'REFUSE_CHEF':
                    status_color = "red"
                    status_text = "Refusé - correction demandée"
                elif statut == 'PUBLIE':
                    status_color = "green"
                    status_text = "Validé et Publié Officiellement"
                elif statut == 'REFUSE_DOYEN':
                    status_color = "red"
                    status_text = "Refusé par le Doyen"
                # Container par formation
                with st.container(border=True):
                    c_title, c_status = st.columns([2, 1])
                    c_title.markdown(f"### {fmt_nom}")
                    c_status.markdown(f"**Statut**: :{status_color}[{status_text}]")
                    st.caption(f"Dernière mise à jour : {date_maj}")
                    
                    # --- Actions ---
                    # 1. Consulter l'EDT (Lecture seule)
                    with st.expander("Consulter l'EDT"):
                        df_details = chef_backend.get_formation_exams_details(fmt_id)
                        if not df_details.empty:
                            st.table(df_details) # Table est plus 'lecture seule' que dataframe editable
                            st.markdown(f"**Total Examens**: {len(df_details)}")
                        else:
                            st.info("Aucun examen dans cet EDT.")

                    # 2. Boutons Validation / Refus
                    # Visible uniquement si EN_ATTENTE_CHEF ou REFUSE_DOYEN (si Admin resoumet) - Mais ici on filtre par get_dept_formations...
                    # Le user demande : "En cliquant sur Valider... Le bouton Refuser devient désactivé"
                    
                    # Si c'est déjà validé ou refusé, on affiche juste l'état, pas les boutons
                    if statut == 'EN_ATTENTE_CHEF':
                        st.write("---")
                        col_btn1, col_btn2 = st.columns(2)
                        
                    if statut == 'EN_ATTENTE_CHEF':
                        st.write("---")
                        col_btn1, col_btn2 = st.columns(2)
                        
                        # Valide
                        with col_btn1:
                             if st.button("Valider et Transmettre", key=f"v_{fmt_id}", use_container_width=True): # Renamed for brevity
                                 s, m = chef_backend.submit_validation(fmt_id, "VALIDE_CHEF", "Valide par le departement")
                                 if s: st.success("Valide !"); time.sleep(0.5); st.rerun()
                                 else: st.error(m)
                        
                        # Refusé -> Ouvre zone commentaire
                        with col_btn2:
                            if st.toggle("Refuser", key=f"toggle_ref_{fmt_id}"): # Removed emoji
                                st.warning("Le refus renverra l'EDT à l'administrateur.")
                                reason = st.text_area("Motif (Obligatoire)", key=f"reason_{fmt_id}")
                                if st.button("Confirmer le Refus", key=f"confirm_ref_{fmt_id}", type="primary", use_container_width=True): # Use width
                                    if not reason.strip():
                                        st.error("Le commentaire est obligatoire.")
                                    else:
                                        s, m = chef_backend.submit_validation(fmt_id, "REFUSE_CHEF", reason)
                                        if s: st.error("Refusé !"); time.sleep(0.5); st.rerun()
                                        else: st.error(m)
                                        
                    elif statut == 'REFUSE_DOYEN':
                        st.error(f"Retour du Doyen : {row['commentaire']}")
                        st.info("En attente de correction par l'Admin.")

        else:
            st.info("Aucun emploi du temps à valider pour le moment. Attendez que l'Administrateur vous les transmette.")

    # --- 2. Alertes & Audit (Lecture Seule) ---
    with tab_audit:
        st.subheader("Alertes de Conformité")
        st.info("Cette section met en évidence les points d'attention potentiels. Ce ne sont pas nécessairement des erreurs bloquantes, mais des éléments à vérifier.")
        
        audit_res = chef_backend.get_department_audit(selected_dept_id)
        
        # Salles (Capacité)
        if 'salles' in audit_res and not audit_res['salles'].empty:
            st.warning(f"{len(audit_res['salles'])} Salles en surcharge potentielle")
            st.table(audit_res['salles'][['salle', 'capacite', 'inscrits', 'module']])
        else:
            st.success("Aucune surcharge de salle détectée.")
            
        st.markdown("---")
        
        # Etudiants (Conflits)
        if 'etudiants' in audit_res and not audit_res['etudiants'].empty:
             st.error(f"{len(audit_res['etudiants'])} Conflits d'horaires étudiants")
             st.table(audit_res['etudiants'])
        else:
             st.success("Aucun conflit d'étudiants détecté.")

    # --- 3. Historique ---
    with tab_hist:
        st.subheader("Historique des Décisions")
        hist = chef_backend.get_validation_history(selected_dept_id)
        if not hist.empty:
            # Formatting history for display
            hist_display = hist.copy()
            hist_display.columns = ["Formation", "Décision", "Commentaire", "Date"]
            st.table(hist_display)
        else:
            st.info("Aucun historique disponible.")



# --- D. INTERFACE PROFESSEUR (SECURE) ---
def interface_prof_secure(prof_id):
    render_user_header()
    
    st.title("Espace Professeurs")
    
    prof_details = public_backend.get_professor_details(prof_id)
    if prof_details is None:
        st.error("Détails introuvables pour votre compte.")
        return

    st.success(f"Bienvenue, **{prof_details['nom']}**")
    
    # Header
    exams = public_backend.get_professor_exams(prof_id)
    
    nb_exams = len(exams)
    nb_days = exams['date_heure'].dt.date.nunique() if not exams.empty else 0
    
    st.markdown("### Résumé")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Professeur", prof_details['nom'])
    c2.metric("Département", prof_details['departement'] if prof_details['departement'] else "N/A")
    c3.metric("Total Examens", nb_exams)
    c4.metric("Jours d'examen", nb_days)
    
    st.divider()

    # Tabs for Personal vs Global Schedule
    tab_perso, tab_global = st.tabs(["Mon Planning", "EDT Global"])
    
    with tab_perso:
        # Planning
        st.markdown("### Mon Planning")
        if not exams.empty:
            exams['Heure'] = exams['date_heure'].dt.strftime('%H:%M') + " - " + (exams['date_heure'] + pd.to_timedelta(exams['duree'], unit='m')).dt.strftime('%H:%M')
            exams['Date'] = exams['date_heure'].dt.strftime('%Y-%m-%d')
            exams['Rôle'] = "Surveillant"
            
            # Renaming for display
            exams = exams.rename(columns={
                'module': 'Module',
                'formation': 'Formation', 
                'salle': 'Salle',
                'type_salle': 'Type'
            })
            
            view_cols = ['Module', 'Formation', 'Date', 'Heure', 'Salle', 'Type', 'Rôle']
            st.dataframe(exams[view_cols], use_container_width=True)
            
            # Alerts
            st.subheader("Alertes")
            alerts = []
            exams_sorted = exams.sort_values('date_heure')
            prev_end = None
            
            for i in range(len(exams_sorted)):
                curr = exams_sorted.iloc[i]
                start = curr['date_heure']
                course_duration = pd.Timedelta(minutes=curr['duree'])
                end = start + course_duration
                
                if i > 0:
                    prev = exams_sorted.iloc[i-1]
                    prev_start = prev['date_heure']
                    prev_duration = pd.Timedelta(minutes=prev['duree'])
                    prev_end_calc = prev_start + prev_duration
                    
                    if start < prev_end_calc:
                        alerts.append(f"CHEVAUCHEMENT : {curr['Module']} ({start}) commence avant la fin de {prev['Module']} ({prev_end_calc})")
                    elif (start - prev_end_calc).total_seconds() < 1800:
                        alerts.append(f"PAUSE COURTE : Moins de 30 min entre {prev['Module']} et {curr['Module']}")
    
                prev_end = end
            
            if alerts:
                for a in alerts:
                    if "CHEVAUCHEMENT" in a: st.error(a)
                    else: st.warning(a)
            else:
                st.success("Aucun conflit horaire détecté.")
    
            # Download
            st.divider()
            if pdf_gen:
                try:
                    pdf_buffer = pdf_gen.generate_schedule_pdf(
                        title=f"Planning Examens - {prof_details['nom']}",
                        subtitle=f"Département: {prof_details['departement']} | Genere le: {datetime.now().strftime('%d/%m/%Y')}",
                        df_schedule=exams_sorted,
                        columns_map={
                            'Module': 'Module',
                            'Formation': 'Formation',
                            'date_heure': 'Date/Heure',
                            'Salle': 'Salle',
                            'Type': 'Type',
                            'Rôle': 'Rôle'
                        }
                    )
                    if pdf_buffer:
                        file_name = f"EDT_Professeur_{prof_details['nom'].replace(' ', '_')}.pdf"
                        st.download_button("Télécharger mon planning (PDF)", data=pdf_buffer, file_name=file_name, mime="application/pdf")
                except Exception as e:
                    st.error(f"Erreur PDF: {e}")
        else:
            st.info("Aucun examen prévu.")

    with tab_global:
        st.subheader("Consulter un autre emploi du temps")
        st.info("Ce mode est en lecture seule.")
        
        col_d, col_f = st.columns(2)
        
        # 1. Select Dept
        all_depts = public_backend.get_all_departments()
        if not all_depts.empty:
            sel_dept_id = col_d.selectbox("Département", all_depts['id'], format_func=lambda x: all_depts[all_depts['id'] == x]['nom'].iloc[0], key="glob_prof_dept")
        else:
            sel_dept_id = None
            col_d.warning("Aucun département trouvé.")
            
        # 2. Select Formation
        sel_fmt_id = None
        if sel_dept_id:
            all_fmts = public_backend.get_formations_by_dept_public(sel_dept_id)
            if not all_fmts.empty:
                sel_fmt_id = col_f.selectbox("Formation", all_fmts['id'], format_func=lambda x: all_fmts[all_fmts['id'] == x]['nom'].iloc[0], key="glob_prof_fmt")
            else:
                col_f.info("Aucune formation dans ce département.")
        
        st.divider()
        
        # 3. Display Schedule
        if sel_fmt_id:
            g_exams = public_backend.get_formation_exams_public(sel_fmt_id)
            if not g_exams.empty:
                g_exams['Date'] = g_exams['date_heure'].dt.strftime('%Y-%m-%d')
                g_exams['Heure'] = g_exams['date_heure'].dt.strftime('%H:%M')
                g_exams['Durée'] = "1h30"
                
                # Rename for display
                g_exams = g_exams.rename(columns={'module': 'Module', 'salle': 'Salle'})
                
                st.dataframe(g_exams[['Module', 'Date', 'Heure', 'Salle', 'Durée']], use_container_width=True)
            else:
                st.info("Aucun examen planifié pour cette formation.")



# --- E. INTERFACE ÉTUDIANT (SECURE) ---
def interface_etudiant_secure(etudiant_id):
    render_user_header()
    
    st.title("Espace Étudiants")
    
    # Fetch Formation from DB directly
    try:
        etu_info = load_data(f"SELECT nom, prenom, formation_id FROM etudiants WHERE id = {etudiant_id}")
    except:
        st.error("Erreur récupération dossier étudiant.")
        return

    if etu_info.empty:
        # Fallback if student ID not found in etudiants table but exists in users
        st.error(f"Dossier étudiant introuvable (ID: {etudiant_id}).")
        return

    etu = etu_info.iloc[0]
    fmt_id = etu['formation_id']
    
    st.success(f"Bienvenue, **{etu['prenom']} {etu['nom']}**")
    
    if not fmt_id:
        st.warning("Vous n'êtes inscrit dans aucune formation.")
        return

    # Get Formation Name
    fmt_df = load_data(f"SELECT nom FROM formations WHERE id = {fmt_id}")
    fmt_name = fmt_df.iloc[0]['nom'] if not fmt_df.empty else "Formation Inconnue"

    tab_perso, tab_global = st.tabs(["Mon Planning", "EDT Global"])

    with tab_perso:
        st.markdown(f"### Votre Planning d'Examens : {fmt_name}")
        
        exams = public_backend.get_formation_exams_public(fmt_id)
        
        if not exams.empty:
            exams['Date'] = exams['date_heure'].dt.strftime('%Y-%m-%d')
            exams['Heure'] = exams['date_heure'].dt.strftime('%H:%M')
            exams['Durée'] = "1h30"
            
            st.dataframe(exams[['module', 'Date', 'Heure', 'salle', 'Durée']], use_container_width=True)
            
            # Download
            if pdf_gen:
                try:
                    pdf_buffer = pdf_gen.generate_schedule_pdf(
                        title=f"Planning Examens - {fmt_name}",
                        subtitle=f"Étudiant: {etu['prenom']} {etu['nom']} | Genere le: {datetime.now().strftime('%d/%m/%Y')}",
                        df_schedule=exams,
                        columns_map={
                            'module': 'Module',
                            'date_heure': 'Date/Heure',
                            'salle': 'Salle',
                            'Durée': 'Durée'
                        }
                    )
                    if pdf_buffer:
                        f_name_clean = fmt_name.replace(" ", "_")
                        st.download_button("Télécharger votre EDT (PDF)", data=pdf_buffer, file_name=f"EDT_{f_name_clean}.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Erreur PDF: {e}")
        else:
            st.info("Aucun examen planifié pour votre formation pour le moment.")

    with tab_global:
        st.subheader("Consulter un autre emploi du temps")
        st.info("Ce mode est en lecture seule.")
        
        col_d, col_f = st.columns(2)
        
        # 1. Select Dept
        all_depts = public_backend.get_all_departments()
        if not all_depts.empty:
            sel_dept_id = col_d.selectbox("Département", all_depts['id'], format_func=lambda x: all_depts[all_depts['id'] == x]['nom'].iloc[0], key="glob_etu_dept")
        else:
            sel_dept_id = None
            col_d.warning("Aucun département trouvé.")
            
        # 2. Select Formation
        sel_fmt_id = None
        if sel_dept_id:
            all_fmts = public_backend.get_formations_by_dept_public(sel_dept_id)
            if not all_fmts.empty:
                sel_fmt_id = col_f.selectbox("Formation", all_fmts['id'], format_func=lambda x: all_fmts[all_fmts['id'] == x]['nom'].iloc[0], key="glob_etu_fmt")
            else:
                col_f.info("Aucune formation dans ce département.")
        
        st.divider()
        
        # 3. Display Schedule
        if sel_fmt_id:
            g_exams = public_backend.get_formation_exams_public(sel_fmt_id)
            if not g_exams.empty:
                g_exams['Date'] = g_exams['date_heure'].dt.strftime('%Y-%m-%d')
                g_exams['Heure'] = g_exams['date_heure'].dt.strftime('%H:%M')
                g_exams['Durée'] = "1h30"
                
                st.dataframe(g_exams[['module', 'Date', 'Heure', 'salle', 'Durée']], use_container_width=True)
            else:
                st.info("Aucun examen planifié pour cette formation.")


# =====================================================
# 3. SYSTÈME DE LOGIN & ROUTAGE GLOBAL
# =====================================================
st.set_page_config(page_title="UMBB Exam System", layout="wide", page_icon="None")

# Init Session
if 'user' not in st.session_state:
    st.session_state.user = None # {id, username, role, ref_id}

def login_screen():
    import backend.auth as auth_backend

    # Layout: 1 column centered with width restriction
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c2: # Center Column
        st.markdown("  ") # Vertical Spacer
        
        with st.container(border=True): # Native Streamlit Card
            # Title inside the card
            st.markdown("<h2 style='text-align: center; color: #0D47A1; border: none;'>Plateforme de Gestion des Examens</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666; margin-bottom: 20px;'>Utilisez vos identifiants universitaires pour accéder à l'espace.</p>", unsafe_allow_html=True)
            
            # --- Diagnostic Connexion (Visible seulement si erreur) ---
            conn_test = auth_backend.get_connection()
            if not conn_test:
                st.error("⚠️ La base de données n'est pas connectée.")
                if not os.getenv("DATABASE_URL"):
                    st.info("💡 Conseil : Le Secret 'DATABASE_URL' semble manquant dans vos paramètres Streamlit Cloud.")
                else:
                    st.info("💡 Conseil : Le lien dans vos Secrets est présent mais Neon refuse la connexion. Vérifiez le mot de passe.")
            else:
                conn_test.close()

            st.markdown("### Se connecter")
            
            with st.form("login_form"):
                email = st.text_input("Email Professionnel", placeholder="")
                pwd = st.text_input("Mot de passe", type="password")
                
                st.write("") # Spacer
                
                if st.form_submit_button("Accéder à la plateforme", type="primary", use_container_width=True):
                    user_data = auth_backend.verify_user(email, pwd)
                    if user_data:
                        st.session_state.user = user_data
                        st.success("Connexion autorisée.")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Échec de l'authentification. Vérifiez vos accès.")

# Router
if st.session_state.user:
    user = st.session_state.user
    role = user['role']
    
    # Routing based on role
    if role == "ADMIN":
        interface_admin()
    elif role == "DOYEN":
        interface_doyen()
    elif role == "CHEF":
        interface_chef_dept(dept_id=user['ref_id'])
    elif role == "PROF":
        interface_prof_secure(prof_id=user['ref_id'])
    elif role == "ETUDIANT":
        interface_etudiant_secure(etudiant_id=user['ref_id'])
    else:
        st.error(f"Rôle inconnu : {role}")

else:
    login_screen()