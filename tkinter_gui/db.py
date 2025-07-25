"""
CuisineCraft Database Handler
Manages SQLite database operations for recipes and ingredients
"""

import sqlite3
import pandas as pd
import logging
import datetime
from typing import List
from models import Recipe, Ingredient, ReceiptItem, WeekMenuEntry
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

logger = logging.getLogger('CuisineCraft')

class DatabaseHandler:
    """Handles all database operations"""
    DB_PATH = os.getenv("DB_PATH", "CuisineCraft.db") # Default to CuisineCraft.db if not found in .env

    def __init__(self):
        self.conn = None
        self.cursor = None
        # Table creation is now handled in connect() to ensure it's always called

    def create_tables(self):
        """Create tables if they don't exist"""
        try:
            logger.debug("Creating tables if they don't exist.")
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS maaltijden (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    recept_naam TEXT NOT NULL UNIQUE,
                    aantal_personen INTEGER,
                    bereidingstijd INTEGER,
                    keuken_origine TEXT,
                    locatie_bestand TEXT,
                    url TEXT,
                    gezondheidsgraad INTEGER
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Ingredienten (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_maaltijden INTEGER,
                    hoeveelheid REAL,
                    eenheid TEXT,
                    ingredient TEXT NOT NULL,
                    prijs REAL,
                    winkel TEXT,
                    datum_prijs INTEGER,
                    FOREIGN KEY (ID_maaltijden) REFERENCES maaltijden(ID)
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ReceiptItems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    shop TEXT,
                    price_date TEXT,
                    quantity REAL,
                    unit TEXT,
                    receipt_image_path TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS WeekMenu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT NOT NULL,
                    recipe_id INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (recipe_id) REFERENCES maaltijden(ID)
                )
            """)
            self.conn.commit()
            logger.info("All tables created or already exist.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create one or more tables: {str(e)}")
            raise

    def connect(self):
        """Establish database connection"""
        try:
            logger.info("Connecting to database...")
            self.conn = sqlite3.connect(self.DB_PATH)
            self.cursor = self.conn.cursor()
            logger.info("Database connection successful.")
            # Ensure tables are created on every connection
            self.create_tables()
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.conn:
            logger.info("Disconnecting from database.")
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def insert_recipe(self, recipe: Recipe) -> int:
        """Insert a new recipe into the database"""
        try:
            logger.info(f"Inserting recipe: {recipe.name}")
            self.cursor.execute("""
                INSERT INTO maaltijden 
                (recept_naam, aantal_personen, bereidingstijd, keuken_origine, 
                locatie_bestand, url, gezondheidsgraad)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (recipe.name, recipe.persons, recipe.cooking_time, 
                  recipe.cuisine_origin, recipe.file_location, 
                  recipe.url, recipe.health_grade))
            self.conn.commit()
            last_id = self.cursor.lastrowid
            logger.info(f"Recipe '{recipe.name}' inserted with ID: {last_id}")
            return last_id
        except sqlite3.Error as e:
            logger.error(f"Failed to insert recipe: {str(e)}")
            self.conn.rollback()
            raise

    def insert_ingredients(self, recipe_id: int, ingredients: List[Ingredient]):
        """Insert ingredients for a recipe"""
        try:
            logger.info(f"Inserting {len(ingredients)} ingredients for recipe ID: {recipe_id}")
            for ingredient in ingredients:
                if not ingredient.amount or not ingredient.name:
                    logger.warning(f"Skipping ingredient with no amount or name for recipe ID: {recipe_id}")
                    continue
                
                # Convert amount to integer to match database schema
                amount_int = int(ingredient.amount)
                
                # Handle date conversion - for now use 0 for empty dates
                date_int = 0  # Default value for date as integer
                if ingredient.price_date:
                    try:
                        # Try to parse date and convert to timestamp
                        if isinstance(ingredient.price_date, str) and ingredient.price_date.strip():
                            date_obj = datetime.datetime.strptime(ingredient.price_date.strip(), '%Y-%m-%d')
                            date_int = int(date_obj.timestamp())
                    except (ValueError, AttributeError):
                        date_int = 0  # Use 0 if date parsing fails
                
                self.cursor.execute("""
                    INSERT INTO Ingredienten 
                    (ID_maaltijden, hoeveelheid, eenheid, ingredient, 
                    prijs, winkel, datum_prijs)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, amount_int, ingredient.unit, 
                      ingredient.name, ingredient.price, ingredient.shop, 
                      date_int))
            self.conn.commit()
            logger.info(f"Successfully inserted {len(ingredients)} ingredients for recipe ID: {recipe_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to insert ingredients: {str(e)}")
            self.conn.rollback()
            raise

    def get_all_recipes(self) -> pd.DataFrame:
        """Get all recipes from database"""
        logger.debug("Fetching all recipes.")
        query = "SELECT * FROM maaltijden ORDER BY ID ASC"
        return pd.read_sql_query(query, self.conn)

    def search_recipes(self, search_term: str) -> pd.DataFrame:
        """Search recipes by name, cuisine, or ingredients"""
        logger.debug(f"Searching recipes with term: {search_term}")
        query = """
            SELECT DISTINCT m.* FROM maaltijden m
            LEFT JOIN Ingredienten i ON m.ID = i.ID_maaltijden
            WHERE LOWER(m.recept_naam) LIKE ? 
               OR LOWER(m.keuken_origine) LIKE ?
               OR LOWER(i.ingredient) LIKE ?
            ORDER BY m.ID ASC
        """
        search_pattern = f'%{search_term.lower()}%'
        return pd.read_sql_query(query, self.conn, params=[search_pattern, search_pattern, search_pattern])

    def get_recipes_for_combo(self) -> pd.DataFrame:
        """Get recipes for combo box selection"""
        logger.debug("Fetching recipes for combobox.")
        query = "SELECT ID, recept_naam FROM maaltijden ORDER BY ID DESC"
        return pd.read_sql_query(query, self.conn)

    def get_latest_recipe_id(self) -> int:
        """Get the ID of the most recently added recipe"""
        logger.debug("Fetching latest recipe ID.")
        result = self.cursor.execute(
            'SELECT ID FROM maaltijden ORDER BY rowid DESC LIMIT 1'
        ).fetchone()
        
        if not result:
            raise ValueError("No recipes found in database")
        
        return result[0]

    def get_ingredients_for_meals(self, meal_names: List[str]) -> List[tuple]:
        """Get aggregated ingredients for a list of meals"""
        logger.debug(f"Fetching ingredients for meals: {meal_names}")
        query = """
            SELECT 
                i.ingredient,
                SUM(i.hoeveelheid) as total_amount,
                i.eenheid
            FROM maaltijden m
            INNER JOIN Ingredienten i ON m.ID = i.ID_maaltijden
            WHERE m.recept_naam IN ({})
            GROUP BY i.ingredient, i.eenheid
            ORDER BY i.ingredient ASC
        """.format(','.join(['?'] * len(meal_names)))
        
        self.cursor.execute(query, meal_names)
        return self.cursor.fetchall()

    def get_week_menu_recipes_with_urls(self, meal_names: List[str]) -> List[dict]:
        """Get recipes for a list of meal names, including their URLs."""
        logger.debug(f"Fetching recipes with URLs for meals: {meal_names}")
        query = """
            SELECT recept_naam, url
            FROM maaltijden
            WHERE recept_naam IN ({})
            ORDER BY recept_naam ASC
        """.format(','.join(['?'] * len(meal_names)))
        
        self.cursor.execute(query, meal_names)
        return [{'name': row[0], 'url': row[1]} for row in self.cursor.fetchall()]

    def get_grouped_ingredients_for_meals(self, meal_names: List[str]) -> dict:
        """Get ingredients grouped by meal for a list of meals."""
        logger.debug(f"Fetching grouped ingredients for meals: {meal_names}")
        if not meal_names:
            return {}

        # Fetch all ingredients for the given meals
        query = """
            SELECT
                m.recept_naam,
                i.ingredient,
                i.hoeveelheid,
                i.eenheid
            FROM maaltijden m
            INNER JOIN Ingredienten i ON m.ID = i.ID_maaltijden
            WHERE m.recept_naam IN ({})
            ORDER BY m.recept_naam, i.ingredient ASC
        """.format(','.join(['?'] * len(meal_names)))
        
        self.cursor.execute(query, meal_names)
        results = self.cursor.fetchall()

        grouped_ingredients = {}
        for meal_name, ingredient_name, amount, unit in results:
            if meal_name not in grouped_ingredients:
                grouped_ingredients[meal_name] = []
            grouped_ingredients[meal_name].append({
                'name': ingredient_name,
                'amount': amount,
                'unit': unit
            })
        return grouped_ingredients

    def get_all_receipt_items(self) -> pd.DataFrame:
        """Get all receipt items from the database"""
        logger.debug("Fetching all receipt items.")
        query = "SELECT * FROM ReceiptItems ORDER BY price_date DESC"
        return pd.read_sql_query(query, self.conn)

    def insert_receipt_items(self, items: List[ReceiptItem]):
        """Insert receipt items into the database"""
        try:
            logger.info(f"Inserting {len(items)} receipt items.")
            for item in items:
                self.cursor.execute("""
                    INSERT INTO ReceiptItems
                    (item_name, price, shop, price_date, quantity, unit, receipt_image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (item.item_name, item.price, item.shop,
                      item.price_date, item.quantity, item.unit, item.receipt_image_path))
            self.conn.commit()
            logger.info(f"Successfully inserted {len(items)} receipt items.")
        except sqlite3.Error as e:
            logger.error(f"Failed to insert receipt items: {str(e)}")
            self.conn.rollback()
            raise

    def insert_week_menu_entry(self, entry: WeekMenuEntry):
        """Insert a new week menu entry into the database"""
        try:
            logger.info(f"Inserting week menu entry for {entry.day}: Recipe ID {entry.recipe_id}")
            self.cursor.execute("""
                INSERT INTO WeekMenu (day, recipe_id, created_at)
                VALUES (?, ?, ?)
            """, (entry.day, entry.recipe_id, entry.created_at))
            self.conn.commit()
            logger.info(f"Successfully inserted week menu entry for {entry.day}.")
        except sqlite3.Error as e:
            logger.error(f"Failed to insert week menu entry: {str(e)}")
            self.conn.rollback()
            raise

    def get_latest_week_menu(self) -> List[WeekMenuEntry]:
        """Get the latest complete week menu (7 entries) from the database."""
        logger.debug("Fetching latest week menu.")
        query = """
            SELECT wm.day, wm.recipe_id, m.recept_naam, m.url
            FROM WeekMenu wm
            JOIN maaltijden m ON wm.recipe_id = m.ID
            ORDER BY wm.created_at DESC, wm.id DESC
            LIMIT 7
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        # Map results to WeekMenuEntry objects (or a more suitable structure for GUI)
        # For now, return a list of dicts for easier GUI consumption
        menu_data = []
        for day, recipe_id, recipe_name, recipe_url in results:
            menu_data.append({
                'day': day,
                'recipe_id': recipe_id,
                'recipe_name': recipe_name,
                'recipe_url': recipe_url
            })
        
        # Ensure we have 7 entries, even if some are missing from DB (fill with None or empty)
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        full_menu = {day: None for day in days_of_week}
        for item in menu_data:
            full_menu[item['day']] = item

        return [full_menu[day] for day in days_of_week]

    def clear_week_menu(self):
        """Clear all entries from the WeekMenu table."""
        try:
            logger.info("Clearing all entries from WeekMenu table.")
            self.cursor.execute("DELETE FROM WeekMenu")
            self.conn.commit()
            logger.info("WeekMenu table cleared successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to clear WeekMenu table: {str(e)}")
            self.conn.rollback()
            raise
