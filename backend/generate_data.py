import random
from datetime import datetime
from backend.db import get_connection

def creation_salles():
    """Genere la structure des salles : 6 blocs, 3 etages, 10 salles par etage."""
    conn = get_connection()
    cur = conn.cursor()
    
    blocs = ['A', 'B', 'C', 'D', 'E', 'F']
    count = 0
    for bloc in blocs:
        for etage in range(3):
            for i in range(1, 11):
                nom = f"Bloc {bloc} - Salle {etage*10 + i}"
                capacite = random.choice([30, 40, 50, 60])
                cur.execute("""
                    INSERT INTO salles (nom, capacite, type) 
                    VALUES (%s, %s, 'Cours')
                """, (nom, capacite))
                count += 1
    
    # Ajout de quelques Amphis
    for i in range(1, 7):
        cur.execute("INSERT INTO salles (nom, capacite, type) VALUES (%s, %s, 'Amphi')", (f"Amphi {i}", 200))
        count += 1

    conn.commit()
    cur.close()
    conn.close()
    return count

def generation_donnees_test():
    """
    Script global pour peupler la base de donnees de test.
    (Utilise uniquement en cas de reset complet)
    """
    pass

if __name__ == "__main__":
    print("Generation structure salles...")
    n = creation_salles()
    print(f"{n} salles creees.")
