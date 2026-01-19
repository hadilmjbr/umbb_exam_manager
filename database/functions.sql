-- =====================================================
-- FONCTIONS ET PROCÉDURES - projet_bda
-- =====================================================


-- Fonction: audit_examens_changes
CREATE OR REPLACE FUNCTION public.audit_examens_changes()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_value, new_value)
        VALUES ('examens', 'UPDATE', OLD.id, ROW(OLD.*)::TEXT, ROW(NEW.*)::TEXT);
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_value, new_value)
        VALUES ('examens', 'DELETE', OLD.id, ROW(OLD.*)::TEXT, NULL);
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_value, new_value)
        VALUES ('examens', 'INSERT', NEW.id, NULL, ROW(NEW.*)::TEXT);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$function$;



-- Fonction: calculer_charge_prof
CREATE OR REPLACE FUNCTION public.calculer_charge_prof(p_prof_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM examens
    WHERE prof_id = p_prof_id;
    RETURN v_count;
END;
$function$;



-- Fonction: check_room_capacity
CREATE OR REPLACE FUNCTION public.check_room_capacity()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_capacite INTEGER;
    v_inscrits INTEGER;
BEGIN
    -- Si salle_id est NULL (pas encore affecté), on ne vérifie pas
    IF NEW.salle_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- Récupérer la capacité de la salle
    SELECT capacite INTO v_capacite FROM salles WHERE id = NEW.salle_id;
    
    -- Récupérer le nombre d'inscrits au module
    SELECT COUNT(*) INTO v_inscrits FROM inscriptions WHERE module_id = NEW.module_id;

    -- Vérification
    IF v_inscrits > v_capacite THEN
        RAISE EXCEPTION 'Capacité insuffisante pour la salle % (Capacité: %, Inscrits: %)', 
            NEW.salle_id, v_capacite, v_inscrits;
    END IF;

    RETURN NEW;
END;
$function$;



-- Fonction: get_nb_inscrits
CREATE OR REPLACE FUNCTION public.get_nb_inscrits(p_module_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM inscriptions
    WHERE module_id = p_module_id;
    RETURN v_count;
END;
$function$;



-- Fonction: verifier_conflit_etudiant
CREATE OR REPLACE FUNCTION public.verifier_conflit_etudiant(p_etudiant_id integer, p_date_heure timestamp without time zone, p_duree_minutes integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_conflit_count INTEGER;
    v_fin_examen TIMESTAMP;
BEGIN
    v_fin_examen := p_date_heure + (p_duree_minutes || ' minutes')::INTERVAL;
    
    SELECT COUNT(*) INTO v_conflit_count
    FROM examens e
    JOIN inscriptions i ON e.module_id = i.module_id
    WHERE i.etudiant_id = p_etudiant_id
    AND (
        (e.date_heure, e.date_heure + (e.duree || ' minutes')::INTERVAL) OVERLAPS (p_date_heure, v_fin_examen)
    );
    
    RETURN v_conflit_count > 0;
END;
$function$;


