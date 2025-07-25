import sqlite3
import sys
from pathlib import Path

def check_database_schema():
    """Check the database schema and compare with the code"""
    
    db_path = Path("tkinter_gui/CuisineCraft.db")
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== DATABASE SCHEMA ===\n")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, name, data_type, not_null, default, pk = col
                print(f"  {name}: {data_type} {'NOT NULL' if not_null else ''} {'PRIMARY KEY' if pk else ''}")
            
            print()
        
        print("\n=== CHECKING CODE COMPATIBILITY ===\n")
        
        # Check maaltijden table compatibility
        print("Checking 'maaltijden' table...")
        cursor.execute("PRAGMA table_info(maaltijden);")
        maaltijden_cols = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_maaltijden_cols = [
            'recept_naam', 'aantal_personen', 'bereidingstijd', 
            'keuken_origine', 'locatie_bestand', 'url', 'gezondheidsgraad'
        ]
        
        for col in expected_maaltijden_cols:
            if col in maaltijden_cols:
                print(f"  ✓ {col}: {maaltijden_cols[col]}")
            else:
                print(f"  ✗ {col}: MISSING")
        
        print()
        
        # Check Ingredienten table compatibility
        print("Checking 'Ingredienten' table...")
        cursor.execute("PRAGMA table_info(Ingredienten);")
        ingredienten_cols = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_ingredienten_cols = [
            'ID_maaltijden', 'hoeveelheid', 'eenheid', 
            'ingredient', 'prijs', 'winkel', 'datum_prijs'
        ]
        
        for col in expected_ingredienten_cols:
            if col in ingredienten_cols:
                print(f"  ✓ {col}: {ingredienten_cols[col]}")
            else:
                print(f"  ✗ {col}: MISSING")
        
        print()
        
        # Check for data type mismatches
        print("=== DATA TYPE ANALYSIS ===\n")
        
        # Check specific potential issues
        issues = []
        
        if 'bereidingstijd' in maaltijden_cols:
            if maaltijden_cols['bereidingstijd'] == 'INTEGER':
                issues.append("WARNING: 'bereidingstijd' is INTEGER but code treats it as TEXT")
        
        if 'hoeveelheid' in ingredienten_cols:
            if ingredienten_cols['hoeveelheid'] == 'INTEGER':
                issues.append("WARNING: 'hoeveelheid' is INTEGER but code expects REAL for float values")
        
        if 'datum_prijs' in ingredienten_cols:
            if ingredienten_cols['datum_prijs'] == 'INTEGER':
                issues.append("WARNING: 'datum_prijs' is INTEGER but code might expect TEXT for dates")
        
        if issues:
            print("POTENTIAL ISSUES FOUND:")
            for issue in issues:
                print(f"  ⚠️  {issue}")
        else:
            print("✓ No obvious data type issues found")
        
        print()
        
        # Sample data check
        print("=== SAMPLE DATA ===\n")
        
        cursor.execute("SELECT COUNT(*) FROM maaltijden")
        meal_count = cursor.fetchone()[0]
        print(f"Total recipes in database: {meal_count}")
        
        cursor.execute("SELECT COUNT(*) FROM Ingredienten")
        ingredient_count = cursor.fetchone()[0]
        print(f"Total ingredients in database: {ingredient_count}")
        
        if meal_count > 0:
            print("\nSample recipe:")
            cursor.execute("SELECT * FROM maaltijden LIMIT 1")
            sample_recipe = cursor.fetchone()
            cursor.execute("PRAGMA table_info(maaltijden)")
            col_names = [row[1] for row in cursor.fetchall()]
            
            for i, value in enumerate(sample_recipe):
                print(f"  {col_names[i]}: {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database_schema()
