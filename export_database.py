"""
Script d'export complet de la base de données PostgreSQL
Génère les fichiers SQL pour le schéma, les données et les fonctions
"""
import psycopg2
from backend.db import get_connection
import os

def export_schema(conn, output_file):
    """Exporte le schéma complet de la base de données"""
    cursor = conn.cursor()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- =====================================================\n")
        f.write("-- SCHÉMA DE LA BASE DE DONNÉES - projet_bda\n")
        f.write("-- =====================================================\n\n")
        
        # Récupérer toutes les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            # Récupérer la définition de chaque table
            cursor.execute(f"""
                SELECT 
                    'CREATE TABLE ' || table_name || ' (' || 
                    string_agg(
                        column_name || ' ' || data_type || 
                        CASE WHEN character_maximum_length IS NOT NULL 
                             THEN '(' || character_maximum_length || ')' 
                             ELSE '' END ||
                        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                        ', '
                    ) || ');'
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                GROUP BY table_name;
            """)
            
            result = cursor.fetchone()
            if result:
                f.write(f"\n-- Table: {table_name}\n")
                f.write(result[0] + "\n")
        
        # Récupérer les contraintes
        f.write("\n\n-- =====================================================\n")
        f.write("-- CONTRAINTES\n")
        f.write("-- =====================================================\n\n")
        
        cursor.execute("""
            SELECT conname, pg_get_constraintdef(oid), conrelid::regclass
            FROM pg_constraint
            WHERE connamespace = 'public'::regnamespace
            ORDER BY conrelid::regclass::text, contype;
        """)
        
        constraints = cursor.fetchall()
        for constraint_name, constraint_def, table_name in constraints:
            f.write(f"-- {table_name}: {constraint_name}\n")
            f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} {constraint_def};\n\n")
    
    cursor.close()
    print(f"✅ Schéma exporté dans: {output_file}")


def export_data(conn, output_file):
    """Exporte toutes les données de la base"""
    cursor = conn.cursor()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- =====================================================\n")
        f.write("-- DONNÉES DE LA BASE DE DONNÉES - projet_bda\n")
        f.write("-- =====================================================\n\n")
        
        # Récupérer toutes les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            f.write(f"\n-- Données pour la table: {table_name}\n")
            
            # Récupérer les noms de colonnes
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            # Récupérer les données
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            # Échapper les apostrophes
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            values.append(f"'{str(val)}'")
                    
                    f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
            else:
                f.write(f"-- Aucune donnée dans {table_name}\n")
    
    cursor.close()
    print(f"✅ Données exportées dans: {output_file}")


def export_functions(conn, output_file):
    """Exporte les fonctions et procédures stockées"""
    cursor = conn.cursor()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- =====================================================\n")
        f.write("-- FONCTIONS ET PROCÉDURES - projet_bda\n")
        f.write("-- =====================================================\n\n")
        
        # Récupérer toutes les fonctions
        cursor.execute("""
            SELECT 
                p.proname as function_name,
                pg_get_functiondef(p.oid) as function_definition
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
            ORDER BY p.proname;
        """)
        
        functions = cursor.fetchall()
        
        if functions:
            for func_name, func_def in functions:
                f.write(f"\n-- Fonction: {func_name}\n")
                f.write(func_def + "\n\n")
        else:
            f.write("-- Aucune fonction définie\n")
    
    cursor.close()
    print(f"✅ Fonctions exportées dans: {output_file}")


def export_complete_database(output_file):
    """Exporte tout dans un seul fichier"""
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    cursor = conn.cursor()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- =====================================================\n")
        f.write("-- EXPORT COMPLET DE LA BASE DE DONNÉES - projet_bda\n")
        f.write(f"-- Date: {__import__('datetime').datetime.now()}\n")
        f.write("-- =====================================================\n\n")
        
        # 1. Schéma
        f.write("\n-- =====================================================\n")
        f.write("-- PARTIE 1: SCHÉMA DES TABLES\n")
        f.write("-- =====================================================\n\n")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            cursor.execute(f"""
                SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns_info = cursor.fetchall()
            
            f.write(f"\nCREATE TABLE {table_name} (\n")
            col_defs = []
            for col_name, data_type, max_len, nullable, default in columns_info:
                col_def = f"    {col_name} {data_type}"
                if max_len:
                    col_def += f"({max_len})"
                if nullable == 'NO':
                    col_def += " NOT NULL"
                if default:
                    col_def += f" DEFAULT {default}"
                col_defs.append(col_def)
            
            f.write(",\n".join(col_defs))
            f.write("\n);\n")
        
        # 2. Contraintes
        f.write("\n\n-- =====================================================\n")
        f.write("-- PARTIE 2: CONTRAINTES\n")
        f.write("-- =====================================================\n\n")
        
        cursor.execute("""
            SELECT conname, pg_get_constraintdef(oid), conrelid::regclass
            FROM pg_constraint
            WHERE connamespace = 'public'::regnamespace
            ORDER BY conrelid::regclass::text;
        """)
        
        for constraint_name, constraint_def, table_name in cursor.fetchall():
            f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} {constraint_def};\n")
        
        # 3. Données
        f.write("\n\n-- =====================================================\n")
        f.write("-- PARTIE 3: DONNÉES\n")
        f.write("-- =====================================================\n\n")
        
        for (table_name,) in tables:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            if rows:
                f.write(f"\n-- Données pour {table_name}\n")
                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(val, (int, float, bool)):
                            values.append(str(val))
                        else:
                            values.append(f"'{str(val)}'")
                    
                    f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
        
        # 4. Fonctions
        f.write("\n\n-- =====================================================\n")
        f.write("-- PARTIE 4: FONCTIONS ET PROCÉDURES\n")
        f.write("-- =====================================================\n\n")
        
        cursor.execute("""
            SELECT pg_get_functiondef(p.oid)
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
            ORDER BY p.proname;
        """)
        
        for (func_def,) in cursor.fetchall():
            f.write(func_def + "\n\n")
    
    cursor.close()
    conn.close()
    print(f"✅ Export complet terminé: {output_file}")


if __name__ == "__main__":
    print("🚀 Démarrage de l'export de la base de données...\n")
    
    # Créer le dossier database s'il n'existe pas
    os.makedirs("database", exist_ok=True)
    
    # Option 1: Export dans des fichiers séparés
    print("📁 Export dans des fichiers séparés:")
    conn = get_connection()
    if conn:
        export_schema(conn, "database/shema.sql")
        export_data(conn, "database/data.sql")
        export_functions(conn, "database/functions.sql")
        conn.close()
    
    # Option 2: Export complet dans un seul fichier
    print("\n📄 Export complet dans un seul fichier:")
    export_complete_database("export_complet.sql")
    
    print("\n✅ Tous les exports sont terminés!")
    print("\n📋 Fichiers générés:")
    print("   - database/shema.sql (schéma des tables)")
    print("   - database/data.sql (toutes les données)")
    print("   - database/functions.sql (fonctions/procédures)")
    print("   - export_complet.sql (tout en un seul fichier)")
