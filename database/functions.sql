
--  FONCTIONS UTILITAIRES

-- Fonction pour calculer la charge d'un professeur (nbr surveillances)
CREATE OR REPLACE FUNCTION calculer_charge_prof(p_prof_id INTEGER) 
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM examens
    WHERE prof_id = p_prof_id;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour vérifier si un étudiant a un conflit à une date donnée
CREATE OR REPLACE FUNCTION verifier_conflit_etudiant(p_etudiant_id INTEGER, p_date_heure TIMESTAMP, p_duree_minutes INTEGER)
RETURNS BOOLEAN AS $$
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
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir le nombre d'inscrits à un module
CREATE OR REPLACE FUNCTION get_nb_inscrits(p_module_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM inscriptions
    WHERE module_id = p_module_id;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- 2. TRIGGERS


-- Trigger pour vérifier la capacité de la salle avant insertion/mise à jour d'un examen
CREATE OR REPLACE FUNCTION check_room_capacity()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_capacity ON examens;
CREATE TRIGGER trg_check_capacity
BEFORE INSERT OR UPDATE OF salle_id, module_id ON examens
FOR EACH ROW
EXECUTE FUNCTION check_room_capacity();


-- Trigger d'audit pour logging des modifications sur les examens (Audit basique)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation VARCHAR(10),
    record_id INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_value TEXT,
    new_value TEXT
);

CREATE OR REPLACE FUNCTION audit_examens_changes()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_examens ON examens;
CREATE TRIGGER trg_audit_examens
AFTER INSERT OR UPDATE OR DELETE ON examens
FOR EACH ROW
EXECUTE FUNCTION audit_examens_changes();


-- 3. INDEXES (Optimisation)


CREATE INDEX IF NOT EXISTS idx_examens_date ON examens(date_heure);
CREATE INDEX IF NOT EXISTS idx_examens_module ON examens(module_id);
CREATE INDEX IF NOT EXISTS idx_examens_prof ON examens(prof_id);
CREATE INDEX IF NOT EXISTS idx_examens_salle ON examens(salle_id);

CREATE INDEX IF NOT EXISTS idx_inscriptions_etudiant ON inscriptions(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_inscriptions_module ON inscriptions(module_id);

CREATE INDEX IF NOT EXISTS idx_etudiants_formation ON etudiants(formation_id);
CREATE INDEX IF NOT EXISTS idx_modules_formation ON modules(formation_id);
