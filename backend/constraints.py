def etudiant_a_examen_ce_jour(cur, etudiant_id, date_exam):
    cur.execute("""
        SELECT COUNT(*)
        FROM examens e
        JOIN inscriptions i ON e.module_id = i.module_id
        WHERE i.etudiant_id = %s
        AND DATE(e.date_heure) = DATE(%s)
    """, (etudiant_id, date_exam))

    return cur.fetchone()[0] > 0


def prof_trop_examens(cur, prof_id, date_exam):
    cur.execute("""
        SELECT COUNT(*)
        FROM examens
        WHERE prof_id = %s
        AND DATE(date_heure) = DATE(%s)
    """, (prof_id, date_exam))

    return cur.fetchone()[0] >= 3


def salle_deja_occupee(cur, salle_id, date_exam):
    cur.execute("""
        SELECT COUNT(*)
        FROM examens
        WHERE salle_id = %s
        AND date_heure = %s
    """, (salle_id, date_exam))

    return cur.fetchone()[0] > 0
