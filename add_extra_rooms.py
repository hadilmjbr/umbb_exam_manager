from backend.db import get_connection

def add_new_rooms():
    print("🏗️ Ajout des nouvelles salles de classe (6 Blocs x 3 Étages x 10 Salles)...")
    
    conn = get_connection()
    if not conn: return

    cur = conn.cursor()
    
    try:
        # On supprime d'abord les anciennes "petites" salles générées pour éviter les doublons/conflits de noms bizarres
        # On garde les Amphis
        cur.execute("DELETE FROM salles WHERE type = 'Salle'")
        print("   - Nettoyage des anciennes salles de TD effectué.")
        
        new_rooms = []
        
        # 6 Blocs
        for b in range(1, 7):
            # 3 Étages
            for etage in range(1, 4): # 1, 2, 3
                # 10 Salles
                for num in range(1, 11):
                    # Format: Bloc 1, Etage 1, Salle 01 -> Salle 1.101
                    # Format: Bloc 2, Etage 3, Salle 10 -> Salle 2.310
                    room_name = f"Salle {b}.{etage}{num:02d}"
                    bloc_name = f"Bloc {b}"
                    # Capacité 40 pour des examens (1 étudiant / table)
                    capacite = 40 
                    
                    new_rooms.append((room_name, capacite, 'Salle', bloc_name))
        
        query = "INSERT INTO salles (nom, capacite, type, bloc) VALUES (%s, %s, %s, %s)"
        cur.executemany(query, new_rooms)
        
        count = len(new_rooms)
        conn.commit()
        print(f"✅ {count} nouvelles salles ajoutées avec succès.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_new_rooms()
