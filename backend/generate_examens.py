from datetime import datetime, timedelta
import random
from backend.db import get_connection
from backend.constraints import (
    etudiant_a_examen_ce_jour,
    prof_trop_examens,
    salle_deja_occupee
)

def generer_examens(date_debut_param, target_formation_id=None):
    """
    Genere les examens selon les regles academiques strictes.
    Si target_formation_id est fourni, regenere UNIQUEMENT pour cette formation
    en tenant compte des autres examens comme contraintes fixes.
    """
    # 1. Parsing Date
    if isinstance(date_debut_param, str):
        date_debut = datetime.strptime(date_debut_param, "%Y-%m-%d")
    elif hasattr(date_debut_param, 'year') and not hasattr(date_debut_param, 'hour'):
        date_debut = datetime.combine(date_debut_param, datetime.min.time())
    else:
        date_debut = date_debut_param

    conn = get_connection()
    cur = conn.cursor()

    # Structures de Suivi
    room_slot_busy = {}
    prof_slot_busy = {}
    prof_day_count = {}
    
    # Recuperer Profs pour init compteurs
    cur.execute("SELECT id, dept_id FROM professeurs")
    profs_data = cur.fetchall()
    prof_total_count = {p[0]: 0 for p in profs_data}

    # 2. Nettoyage et Init Contraintes
    if target_formation_id:
        print(f"Regeneration ciblee pour la formation {target_formation_id}...")
        
        # a. Supprimer uniquement les examens de cette formation
        cur.execute("""
            DELETE FROM examens 
            WHERE module_id IN (SELECT id FROM modules WHERE formation_id = %s)
        """, (target_formation_id,))
        
        # b. Charger les contraintes des AUTRES examens existants
        cur.execute("""
            SELECT e.salle_id, e.prof_id, e.date_heure 
            FROM examens e
        """)
        existing_exams = cur.fetchall()
        
        for s_id, p_id, dt in existing_exams:
            # Busy Rooms
            if s_id:
                if s_id not in room_slot_busy: room_slot_busy[s_id] = set()
                room_slot_busy[s_id].add(dt)
            
            # Busy Profs
            if p_id:
                if p_id not in prof_slot_busy: prof_slot_busy[p_id] = set()
                prof_slot_busy[p_id].add(dt)
                
                d = dt.date()
                if p_id not in prof_day_count: prof_day_count[p_id] = {}
                prof_day_count[p_id][d] = prof_day_count[p_id].get(d, 0) + 1
                
                if p_id in prof_total_count:
                    prof_total_count[p_id] += 1

    else:
        # Full Regen
        cur.execute("DELETE FROM examens")
        cur.execute("DELETE FROM validation_pedagogique") # RESET VALIDATIONS
        print("Anciens examens et validations supprimés (Full Reset).")

    conn.commit()

    # 3. Recuperation Modules a planifier
    query_modules = """
        SELECT m.id, m.formation_id, COUNT(i.etudiant_id) as nb_inscrits, f.dept_id
        FROM modules m
        JOIN formations f ON m.formation_id = f.id
        LEFT JOIN inscriptions i ON m.id = i.module_id
    """
    params = []
    if target_formation_id:
        query_modules += " WHERE m.formation_id = %s"
        params.append(target_formation_id)
        
    query_modules += " GROUP BY m.id, m.formation_id, f.dept_id ORDER BY nb_inscrits DESC"
    
    cur.execute(query_modules, params)
    modules_data = cur.fetchall()

    if not modules_data:
        print("Aucun module à planifier.")
        return

    # Salles
    cur.execute("SELECT id, capacite, type FROM salles ORDER BY capacite DESC")
    salles_data = cur.fetchall()

    # 4. Structures de Suivi (Formation context)
    formation_last_date = {} 
    formation_assigned_slot = {}
    
    # Creneaux
    slots_horaires = [(8, 0), (10, 0), (12, 0), (14, 0)]
    duree_exam = 90

    # 5. Algorithme
    current_day = date_debut
    max_days = 90
    exams_to_schedule = list(modules_data)
    
    count_placed = 0
    
    for mod_id, fmt_id, nb_inscrits, mod_dept_id in exams_to_schedule:
        place = False
        search_date = date_debut 
        
        modes = ['strict'] 
        max_room_cap = salles_data[0][1] if salles_data else 0
        if nb_inscrits > max_room_cap: modes = ['relaxed']

        for mode in modes:
            if place: break
            if mode == 'relaxed': search_date = date_debut 
            
            while not place and (search_date - date_debut).days < max_days:
                # No Friday
                if search_date.weekday() == 4:
                    search_date += timedelta(days=1)
                    continue
                
                # Intervalle 2 jours (Intra-formation logic)
                last_date = formation_last_date.get(fmt_id)
                if last_date and (search_date.date() - last_date).days < 2:
                    search_date += timedelta(days=1)
                    continue

                curr_date_only = search_date.date()
                
                daily_slots = []
                if fmt_id in formation_assigned_slot:
                    daily_slots = [formation_assigned_slot[fmt_id]]
                else:
                    daily_slots = list(slots_horaires)
                    random.shuffle(daily_slots)

                for h, m in daily_slots:
                    slot_dt = search_date.replace(hour=h, minute=m, second=0)
                    
                    # Selection Aleatoire de la salle parmi les candidates valides
                    candidates_salles = []
                    for s_id, s_cap, s_type in salles_data:
                        if mode == 'strict' and s_cap < nb_inscrits: continue
                        # Check Global Busy
                        if s_id in room_slot_busy and slot_dt in room_slot_busy[s_id]: continue
                        
                        candidates_salles.append(s_id)
                    
                    if not candidates_salles: continue
                    chosen_salle = random.choice(candidates_salles)

                    # Check Prof
                    candidates = []
                    for p_id, p_dept_id in profs_data:
                        # Global Busy
                        if p_id in prof_slot_busy and slot_dt in prof_slot_busy[p_id]: continue
                        
                        # Max 3/day
                        p_daily = prof_day_count.get(p_id, {}).get(curr_date_only, 0)
                        if p_daily >= 3: continue
                        
                        score = 0
                        if p_dept_id == mod_dept_id: score += 100
                        score -= prof_total_count[p_id]
                        candidates.append((score, p_id))
                    
                    if not candidates: continue
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    chosen_prof = candidates[0][1]

                    # Insert
                    cur.execute("""
                        INSERT INTO examens (module_id, prof_id, salle_id, date_heure, duree)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (mod_id, chosen_prof, chosen_salle, slot_dt, duree_exam))

                    # Update State
                    formation_last_date[fmt_id] = curr_date_only
                    if fmt_id not in formation_assigned_slot:
                        formation_assigned_slot[fmt_id] = (h, m)

                    if chosen_salle not in room_slot_busy: room_slot_busy[chosen_salle] = set()
                    room_slot_busy[chosen_salle].add(slot_dt)

                    if chosen_prof not in prof_slot_busy: prof_slot_busy[chosen_prof] = set()
                    prof_slot_busy[chosen_prof].add(slot_dt)

                    if chosen_prof not in prof_day_count: prof_day_count[chosen_prof] = {}
                    prof_day_count[chosen_prof][curr_date_only] = prof_day_count[chosen_prof].get(curr_date_only, 0) + 1
                    prof_total_count[chosen_prof] += 1

                    place = True
                    count_placed += 1
                    break 
                
                if not place: search_date += timedelta(days=1)
            
            if not place and mode == 'strict': modes.append('relaxed')
        
        if not place:
            print(f"Impossible de placer le module {mod_id}")

    conn.commit()
    
    # Update timestamp
    try:
        cur.execute("INSERT INTO parametres (cle, valeur) VALUES ('last_generation', %s) ON CONFLICT (cle) DO UPDATE SET valeur = EXCLUDED.valeur", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
        
        # Initialiser statut BROUILLON pour la/les formations concernees
        if target_formation_id:
            cur.execute("""
                INSERT INTO validation_pedagogique (formation_id, statut, date_maj)
                VALUES (%s, 'BROUILLON', CURRENT_TIMESTAMP)
                ON CONFLICT (formation_id) DO UPDATE SET statut = 'BROUILLON', date_maj = CURRENT_TIMESTAMP
            """, (target_formation_id,))
        else:
            cur.execute("SELECT DISTINCT formation_id FROM modules WHERE id IN (SELECT module_id FROM examens)")
            fmts = cur.fetchall()
            for f in fmts:
                cur.execute("""
                    INSERT INTO validation_pedagogique (formation_id, statut, date_maj)
                    VALUES (%s, 'BROUILLON', CURRENT_TIMESTAMP)
                    ON CONFLICT (formation_id) DO UPDATE SET statut = 'BROUILLON', date_maj = CURRENT_TIMESTAMP
                """, (f[0],))
            
        conn.commit()
    finally:
        cur.close()
        conn.close()
    print(f"Done: {count_placed} exams scheduled.")

if __name__ == "__main__":
    generer_examens(datetime(2026, 6, 1))
