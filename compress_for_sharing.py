# Script de compression de la base de données pour envoi
# Usage: python compress_for_sharing.py

import zipfile
import os
from datetime import datetime

def compress_database_files():
    """Compresse les fichiers de la base de données pour partage"""
    
    # Nom du fichier zip avec date
    date_str = datetime.now().strftime("%Y%m%d")
    zip_filename = f"projet_bda_database_{date_str}.zip"
    
    # Fichiers à inclure
    files_to_compress = [
        "export_complet.sql",
        "README_INSTALLATION_BDD.md",
        "requirements.txt"
    ]
    
    # Optionnel : inclure aussi les fichiers séparés
    database_files = [
        "database/shema.sql",
        "database/data.sql",
        "database/functions.sql"
    ]
    
    print("🗜️  Compression des fichiers de la base de données...")
    print(f"📦 Création de : {zip_filename}\n")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter les fichiers principaux
        for file in files_to_compress:
            if os.path.exists(file):
                zipf.write(file, arcname=file)
                size = os.path.getsize(file) / (1024 * 1024)  # MB
                print(f"✅ Ajouté : {file} ({size:.2f} MB)")
            else:
                print(f"⚠️  Fichier non trouvé : {file}")
        
        # Ajouter les fichiers du dossier database (optionnel)
        print("\n📁 Ajout des fichiers database/ (optionnel)...")
        for file in database_files:
            if os.path.exists(file):
                zipf.write(file, arcname=file)
                size = os.path.getsize(file) / 1024  # KB
                print(f"✅ Ajouté : {file} ({size:.2f} KB)")
    
    # Afficher la taille finale
    final_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    print(f"\n✅ Compression terminée !")
    print(f"📦 Fichier créé : {zip_filename}")
    print(f"📊 Taille finale : {final_size:.2f} MB")
    print(f"\n💡 Vous pouvez maintenant envoyer ce fichier par email, Google Drive, etc.")
    print(f"📧 Le destinataire devra suivre les instructions dans README_INSTALLATION_BDD.md")

if __name__ == "__main__":
    compress_database_files()
