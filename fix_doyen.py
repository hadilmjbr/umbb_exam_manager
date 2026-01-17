"""
Diagnostic précis du compte doyen
"""
from backend.db import get_connection
from backend.auth import hash_password

conn = get_connection()
if conn:
    cur = conn.cursor()
    
    print("="*60)
    print("DIAGNOSTIC COMPTE DOYEN")
    print("="*60)
    
    # Chercher le doyen
    cur.execute("SELECT id, username, email, password_hash, role FROM users WHERE username = 'doyen' OR email = 'doyen@umbb.dz'")
    doyen = cur.fetchone()
    
    if doyen:
        print(f"\n✅ Utilisateur trouvé:")
        print(f"   ID: {doyen[0]}")
        print(f"   Username: {doyen[1]}")
        print(f"   Email: {doyen[2]}")
        print(f"   Password Hash (DB): {doyen[3][:20]}...")
        print(f"   Role: {doyen[4]}")
        
        # Test des mots de passe possibles
        test_passwords = ["123456", "admin123", "doyen", "doyen123"]
        
        print(f"\n🔐 Test de mots de passe:")
        for pwd in test_passwords:
            test_hash = hash_password(pwd)
            match = (test_hash == doyen[3])
            status = "✅ MATCH!" if match else "❌"
            print(f"   {status} '{pwd}': {test_hash[:20]}...")
        
        # Mettre à jour le mot de passe à 123456
        print(f"\n🔧 Mise à jour du mot de passe doyen -> '123456'")
        new_hash = hash_password("123456")
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, doyen[0]))
        conn.commit()
        print(f"   ✅ Mot de passe mis à jour")
        
    else:
        print("\n❌ Aucun utilisateur doyen trouvé!")
        print("\n🔧 Création du compte doyen...")
        doyen_hash = hash_password("123456")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, ref_id)
            VALUES ('doyen', 'doyen@umbb.dz', %s, 'DOYEN', NULL)
        """, (doyen_hash,))
        conn.commit()
        print("   ✅ Compte doyen créé: doyen@umbb.dz / 123456")
    
    # Test final
    print(f"\n✅ TEST FINAL:")
    test_hash = hash_password("123456")
    cur.execute("""
        SELECT id, username, email, role 
        FROM users 
        WHERE email = 'doyen@umbb.dz' AND password_hash = %s
    """, (test_hash,))
    result = cur.fetchone()
    
    if result:
        print(f"   ✅ Authentification réussie!")
        print(f"   User: {result}")
    else:
        print(f"   ❌ Authentification échouée")
    
    conn.close()
    
    print("\n" + "="*60)
    print("ESSAYEZ MAINTENANT: doyen@umbb.dz / 123456")
    print("="*60)
else:
    print("❌ Connexion impossible")
