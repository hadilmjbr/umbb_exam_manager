from backend.db import get_connection
from datetime import datetime

def regenerate_formation_schedule(formation_id):
    """
    Régénère l'EDT d'une formation spécifique, reset le statut et le commentaire.
    """
    # Import local pour garantir le rechargement du module modifié
    from backend.generate_examens import generer_examens
    conn = get_connection()
    if not conn: return False, "Erreur connexion BDD"
    
    try:
        # 1. Détecter la date de début réelle de la session (basée sur les autres examens)
        # Cela garantit qu'on reste dans la même "période d'examens"
        start_date = datetime(2026, 6, 1) # Default fallback
        cur = conn.cursor()
        
        cur.execute("SELECT MIN(DATE(date_heure)) FROM examens")
        row = cur.fetchone()
        if row and row[0]:
            start_date = datetime.combine(row[0], datetime.min.time())
            print(f"📅 Date de début détectée via BDD : {start_date}")
        else:
            # Fallback 2: Parametres
            cur.execute("SELECT valeur FROM parametres WHERE cle = 'date_debut_examens'")
            row_p = cur.fetchone()
            if row_p:
                try:
                    start_date = datetime.strptime(row_p[0], "%Y-%m-%d")
                except: pass
            print(f"📅 Date de début par défaut/param : {start_date}")

        print(f"Lancement régénération pour formation {formation_id} à partir de {start_date}")
        generer_examens(start_date, target_formation_id=formation_id)
        
        # 2. Update Statut
        cur.execute("""
            UPDATE validation_pedagogique
            SET statut = 'EN_ATTENTE_CHEF', commentaire = NULL, date_maj = CURRENT_TIMESTAMP
            WHERE formation_id = %s
        """, (formation_id,))
        
        conn.commit()
        cur.close()
        return True, "EDT régénéré et renvoyé au Chef !"
        
    except Exception as e:
        return False, f"Erreur régénération: {e}"
    finally:
        conn.close()
