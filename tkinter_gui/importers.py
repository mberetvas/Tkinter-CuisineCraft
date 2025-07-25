"""
CuisineCraft Recipe Importers Module
Handles fetching and parsing recipes from external URLs.
"""

import requests
import re
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse

from models import Recipe
from constants import SUPPORTED_DOMAINS

def parse_15gram_recipe(html_content: str, url: str) -> Optional[Recipe]:
    """Parses recipe data from 15gram.be HTML content."""
    soup = BeautifulSoup(html_content, 'lxml')

    # Extract Title
    title_tag = soup.find('h1')
    name = title_tag.get_text(strip=True) if title_tag else "Unknown Recipe"

    # Extract Persons and Cooking Time
    persons = 0
    cooking_time = 0
    info_text = soup.find(text=re.compile(r'\d+\s*MIN|\d+\s*personen'))
    if info_text:
        time_match = re.search(r'(\d+)\s*MIN', info_text)
        if time_match:
            cooking_time = int(time_match.group(1))
        persons_match = re.search(r'(\d+)\s*personen', info_text)
        if persons_match:
            persons = int(persons_match.group(1))

    # Extract Cuisine Origin (default to "Belgian" for 15gram.be)
    cuisine_origin = "Belgian"

    # Extract File Location (will be empty for imported recipes)
    file_location = ""

    # Extract Health Grade (default to 0 for imported recipes)
    health_grade = 0

    # For ingredients and instructions, we need to find specific sections.
    ingredients_list = []
    instructions_text = ""

    ingredients_heading = soup.find('h3', string='Ingrediënten')
    if ingredients_heading:
        ul = ingredients_heading.find_next('ul')
        if ul:
            for li in ul.find_all('li'):
                ingredients_list.append(li.get_text(strip=True))

    instructions_heading = soup.find('h3', string='BEREIDING')
    if instructions_heading:
        next_sibling = instructions_heading.find_next_sibling()
        while next_sibling and next_sibling.name in ['ol', 'p']:
            if next_sibling.name == 'ol':
                for li in next_sibling.find_all('li'):
                    instructions_text += li.get_text(strip=True) + "\n"
            elif next_sibling.name == 'p':
                instructions_text += next_sibling.get_text(strip=True) + "\n"
            next_sibling = next_sibling.find_next_sibling()

    combined_content = f"Ingredients:\n{'- ' + '\\n- '.join(ingredients_list)}\n\nInstructions:\n{instructions_text.strip()}"
    
    # Create a temporary file to store the recipe content
    temp_file_path = f"temp_recipe_{name.replace(' ', '_')}.txt"
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(combined_content)
    file_location = temp_file_path

    return Recipe(
        name=name,
        persons=persons,
        cooking_time=cooking_time,
        cuisine_origin=cuisine_origin,
        file_location=file_location,
        url=url,
        health_grade=health_grade
    )

def import_recipe_from_url(url: str, status_bar, import_feedback_label, db_handler, refresh_recipe_list_func, populate_recipe_combo_func, url_entry_clear_func) -> None:
    """Fetch a recipe from a supported URL, parse, and add to the database."""
    import tkinter.messagebox as messagebox # Import here to avoid circular dependency if gui imports importers
    
    import_feedback_label.config(text="")
    status_bar.set_status("Importing recipe...", show_progress=True)
    try:
        # Validate URL
        if not url:
            import_feedback_label.config(text="Please enter a recipe URL.")
            status_bar.set_status("No URL entered")
            return
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        if domain not in SUPPORTED_DOMAINS:
            import_feedback_label.config(text=f"Unsupported domain: {domain}")
            status_bar.set_status("Unsupported domain")
            return

        # Fetch HTML
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            import_feedback_label.config(text=f"Failed to fetch page: {response.status_code}")
            status_bar.set_status("Failed to fetch page")
            return

        # Parse recipe
        parser_func_name = SUPPORTED_DOMAINS[domain]
        parser_func = globals()[parser_func_name] # Get function by name
        recipe = parser_func(response.text, url)
        if not recipe:
            import_feedback_label.config(text="Failed to parse recipe from page.")
            status_bar.set_status("Parse error")
            return

        # Insert into database
        with db_handler() as db:
            db.insert_recipe(recipe)

        import_feedback_label.config(text="Recipe imported successfully!")
        status_bar.set_status("Recipe imported successfully!")
        messagebox.showinfo("Success", "Recipe imported and added to database.")
        refresh_recipe_list_func()
        populate_recipe_combo_func()
        url_entry_clear_func()
    except Exception as e:
        import_feedback_label.config(text=f"Error: {str(e)}")
        status_bar.set_status(f"Error importing recipe: {str(e)}")
    finally:
        status_bar.set_status("Ready")