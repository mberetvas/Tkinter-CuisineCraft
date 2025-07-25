"""
CuisineCraft Main GUI Module
Refactored from CuisineCraft_Modern.py with modular structure
"""

from tkinter_gui.models import Recipe, WeekMenuEntry
from tkinter_gui.db import DatabaseHandler
from tkinter_gui.theme import ModernTheme, ToolTip, StatusBar
from tkinter_gui.widgets.modern_entry import ModernEntry
from tkinter_gui.widgets.ingredient_entry import ModernIngredientEntry
from tkinter_gui.utils import parse_cooking_time, export_to_text, export_to_csv
import tkinter as tk
import pandas as pd
from tkinter_gui.logger import logger
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
# Removed requests, BeautifulSoup, urlparse as they are now in importers.py

load_dotenv()  # Load environment variables from .env file


class CuisineCraftModernGUI:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseHandler()

        # Configure window
        self.root.title("CuisineCraft - Recipe Manager")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=ModernTheme.COLORS["background"])

        # Apply modern theme
        ModernTheme.configure_style(root)

        # Setup menu bar
        self.setup_menu_bar()

        # Main container
        self.main_frame = ttk.Frame(root, style="Modern.TFrame")
        self.main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        self.setup_header()

        # Notebook (tabs)
        self.setup_notebook()

        # Status bar
        self.setup_status_bar()

        # Initialize ingredient entries list before setting up tabs
        self.ingredient_entries: List[ModernIngredientEntry] = []

        # Initialize list to hold comboboxes for manual week menu
        self.manual_week_menu_recipe_combos = {}

        # Initialize tabs
        self.setup_recipe_list_tab()
        self.setup_week_menu_tab()  # This is the random generator tab
        self.setup_manual_week_menu_tab()  # New tab for manual selection
        self.setup_recipe_tab()
        self.setup_ingredients_tab()
        self.setup_import_recipe_tab()  # New tab for importing recipes

        # Load initial data
        self.refresh_recipe_list()

    def setup_header(self):
        """Create modern header with title and branding"""
        header_frame = ttk.Frame(self.main_frame, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 16))

        # Title
        title = ttk.Label(
            header_frame,
            text="CuisineCraft",
            style="Heading.TLabel",
            font=("Segoe UI", 24, "bold"),
        )
        title.pack(side="left")

        # Subtitle
        subtitle = ttk.Label(
            header_frame,
            text="Professional Recipe Manager",
            style="Modern.TLabel",
            font=ModernTheme.FONTS["body"],
        )
        subtitle.pack(side="left", padx=(8, 0), pady=(8, 0))

    def setup_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = StatusBar(self.main_frame)
        self.status_bar.pack(fill="x", side="bottom", pady=(8, 0))

    def setup_notebook(self):
        """Create modern tabbed interface"""
        self.notebook = ttk.Notebook(self.main_frame, style="Modern.TNotebook")
        self.notebook.pack(expand=True, fill="both")

        # Create tab frames
        self.tab_recipes = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.tab_week_menu = ttk.Frame(
            self.notebook, style="Modern.TFrame"
        )  # Random generator
        self.tab_manual_week_menu = ttk.Frame(
            self.notebook, style="Modern.TFrame"
        )  # Manual selection
        self.tab_add_recipe = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.tab_ingredients = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.tab_import_recipe = ttk.Frame(
            self.notebook, style="Modern.TFrame"
        )  # New tab frame

        # Add tabs with modern styling
        self.notebook.add(self.tab_recipes, text="📋 Recipe List")
        self.notebook.add(
            self.tab_week_menu, text="🎲 Auto Menu"
        )  # Renamed for clarity
        self.notebook.add(self.tab_manual_week_menu, text="✍️ Manual Menu")  # New tab
        self.notebook.add(self.tab_add_recipe, text="➕ Add Recipe")
        self.notebook.add(self.tab_ingredients, text="🥕 Add Ingredients")
        self.notebook.add(self.tab_import_recipe, text="🔗 Import Recipe")  # New tab

    def setup_recipe_list_tab(self):
        """Modern recipe list with search and filters"""
        # Configure tab padding
        self.tab_recipes.configure(padding=16)

        # Search frame
        search_frame = ttk.Frame(self.tab_recipes, style="Card.TFrame")
        search_frame.pack(fill="x", pady=(0, 16))
        search_frame.configure(padding=12)

        search_label = ttk.Label(
            search_frame,
            text="Search Recipes",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        search_label.pack(anchor="w", pady=(0, 8))

        self.search_entry = ModernEntry(
            search_frame, placeholder="Search by name, cuisine, or ingredient..."
        )
        self.search_entry.pack(fill="x")

        # Bind search to real-time filtering
        self.search_entry.entry.bind("<KeyRelease>", self.on_search_change)

        # Recipe list frame
        list_frame = ttk.Frame(self.tab_recipes, style="Card.TFrame")
        list_frame.pack(fill="both", expand=True)
        list_frame.configure(padding=12)

        # List header
        list_header = ttk.Label(
            list_frame,
            text="Your Recipes",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        list_header.pack(anchor="w", pady=(0, 8))

        # Listbox with modern styling
        listbox_frame = ttk.Frame(list_frame, style="Card.TFrame")
        listbox_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.recipe_listbox = tk.Listbox(
            listbox_frame,
            font=ModernTheme.FONTS["body"],
            bg=ModernTheme.COLORS["surface"],
            fg=ModernTheme.COLORS["text_primary"],
            selectbackground=ModernTheme.COLORS["primary_light"],
            selectforeground=ModernTheme.COLORS["surface"],
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
        )

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.recipe_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.recipe_listbox.yview)
        self.recipe_listbox.pack(fill="both", expand=True)

        # Action buttons
        button_frame = ttk.Frame(list_frame, style="Card.TFrame")
        button_frame.pack(fill="x")

        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh List",
            style="Modern.TButton",
            command=self.refresh_recipe_list,
        )
        refresh_btn.pack(side="left", padx=(0, 8))
        ToolTip(refresh_btn, "Refresh the recipe list (Ctrl+R)")

        search_btn = ttk.Button(
            button_frame,
            text="🔍 Search",
            style="Secondary.TButton",
            command=self.search_recipes,
        )
        search_btn.pack(side="left")
        ToolTip(search_btn, "Search recipes by name, cuisine, or ingredient")

    def setup_week_menu_tab(self):
        """Modern week menu generator with enhanced UI"""
        self.tab_week_menu.configure(padding=16)

        # Generator section
        generator_frame = ttk.Frame(self.tab_week_menu, style="Card.TFrame")
        generator_frame.pack(fill="x", pady=(0, 16))
        generator_frame.configure(padding=12)

        gen_label = ttk.Label(
            generator_frame,
            text="Week Menu Generator",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        gen_label.pack(anchor="w", pady=(0, 12))

        # Controls
        controls_frame = ttk.Frame(generator_frame, style="Card.TFrame")
        controls_frame.pack(fill="x", pady=(0, 12))

        generate_btn = ttk.Button(
            controls_frame,
            text="🎲 Generate Week Menu",
            style="Modern.TButton",
            command=self.generate_week_menu,
        )
        generate_btn.pack(side="left", padx=(0, 8))
        ToolTip(generate_btn, "Generate a random 7-day menu (Ctrl+G)")

        export_btn = ttk.Button(
            controls_frame,
            text="📤 Export Menu",
            style="Secondary.TButton",
            command=self.export_week_menu,
        )
        export_btn.pack(side="left")
        ToolTip(export_btn, "Export menu and shopping list to file (Ctrl+E)")

        remove_selected_btn = ttk.Button(
            controls_frame,
            text="🗑️ Remove Selected",
            style="Danger.TButton",
            command=self.remove_selected_menu_items,
        )
        remove_selected_btn.pack(side="left", padx=(8, 0))
        ToolTip(remove_selected_btn, "Remove selected recipes from the week menu")

        # Week menu display
        menu_frame = ttk.Frame(self.tab_week_menu, style="Card.TFrame")
        menu_frame.pack(fill="x", pady=(0, 16))
        menu_frame.configure(padding=12)

        menu_label = ttk.Label(
            menu_frame,
            text="This Week's Menu",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        menu_label.pack(anchor="w", pady=(0, 8))

        self.week_menu_listbox = tk.Listbox(
            menu_frame,
            font=ModernTheme.FONTS["body"],
            bg=ModernTheme.COLORS["surface"],
            fg=ModernTheme.COLORS["text_primary"],
            selectbackground=ModernTheme.COLORS["primary_light"],
            borderwidth=0,
            highlightthickness=0,
            height=8,
        )
        self.week_menu_listbox.pack(fill="x", pady=(0, 8))

        # Ingredients section
        ingredients_frame = ttk.Frame(self.tab_week_menu, style="Card.TFrame")
        ingredients_frame.pack(fill="both", expand=True)
        ingredients_frame.configure(padding=12)

        ing_label = ttk.Label(
            ingredients_frame,
            text="Shopping List",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        ing_label.pack(anchor="w", pady=(0, 8))

        # Modern treeview
        tree_frame = ttk.Frame(ingredients_frame, style="Card.TFrame")
        tree_frame.pack(fill="both", expand=True)

        self.ingredients_tree = ttk.Treeview(
            tree_frame,
            columns=("ingredients", "amount", "unit", "price", "shop"),
            show="headings",
            style="Modern.Treeview",
        )

        self.ingredients_tree.heading("ingredients", text="Ingredient")
        self.ingredients_tree.heading("amount", text="Amount")
        self.ingredients_tree.heading("unit", text="Unit")
        self.ingredients_tree.heading("price", text="Est. Price")
        self.ingredients_tree.heading("shop", text="Shop")

        self.ingredients_tree.column("ingredients", width=200)
        self.ingredients_tree.column("amount", width=80)
        self.ingredients_tree.column("unit", width=80)
        self.ingredients_tree.column("price", width=80)
        self.ingredients_tree.column("shop", width=100)

        tree_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.ingredients_tree.yview
        )
        tree_scrollbar.pack(side="right", fill="y")
        self.ingredients_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.ingredients_tree.pack(fill="both", expand=True)

    def setup_recipe_tab(self):
        """Modern recipe addition form"""
        self.tab_add_recipe.configure(padding=16)

        # Scrollable frame for long forms
        canvas = tk.Canvas(
            self.tab_add_recipe,
            bg=ModernTheme.COLORS["background"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            self.tab_add_recipe, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas, style="Modern.TFrame")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form header
        header_frame = ttk.Frame(scrollable_frame, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 16))

        form_header = ttk.Label(
            header_frame, text="Add New Recipe", style="Heading.TLabel"
        )
        form_header.pack(anchor="w")

        # Form fields
        self.recipe_entries = {}
        fields = [
            ("name", "Recipe Name", "Enter recipe name"),
            ("persons", "Number of Persons", "Enter number of persons"),
            ("cooking_time", "Cooking Time", "e.g., 30 minutes"),
            ("cuisine_origin", "Cuisine Origin", "e.g., Italian"),
            ("file_location", "File Location", "Path to recipe file"),
            ("url", "Recipe URL", "Optional recipe URL"),
            ("health_grade", "Health Grade (1-3, 1 being healthiest)", "1-3"),
        ]

        # Create input fields
        for field, label, placeholder in fields:
            frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
            frame.pack(fill="x", pady=(0, 12))
            frame.configure(padding=12)

            entry = ModernEntry(
                frame, label_text=label, placeholder=placeholder, width=100
            )
            entry.pack(fill="x")
            self.recipe_entries[field] = entry

        # Form buttons
        button_frame = ttk.Frame(scrollable_frame, style="Modern.TFrame")
        button_frame.pack(fill="x", pady=(16, 0))

        save_btn = ttk.Button(
            button_frame,
            text="💾 Save Recipe",
            style="Modern.TButton",
            command=self.save_recipe,
        )
        save_btn.pack(side="left", padx=(0, 8))

        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Form",
            style="Secondary.TButton",
            command=self.clear_recipe_form,
        )
        clear_btn.pack(side="left")

    def setup_ingredients_tab(self):
        """Modern ingredients form"""
        self.tab_ingredients.configure(padding=16)

        # Scrollable frame for ingredient entries
        canvas = tk.Canvas(
            self.tab_ingredients,
            bg=ModernTheme.COLORS["background"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            self.tab_ingredients, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas, style="Modern.TFrame")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header
        header_frame = ttk.Frame(scrollable_frame, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 16))

        header = ttk.Label(header_frame, text="Add Ingredients", style="Heading.TLabel")
        header.pack(anchor="w")

        # Instructions
        instruction_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        instruction_frame.pack(fill="x", pady=(0, 16))
        instruction_frame.configure(padding=12)

        instructions = ttk.Label(
            instruction_frame,
            text="Enter ingredients with amount, unit, and name. Price is optional.",
            style="Card.TLabel",
        )
        instructions.pack(anchor="w")

        # Ingredient entries container
        self.entries_frame = ttk.Frame(scrollable_frame, style="Modern.TFrame")
        self.entries_frame.pack(fill="x")

        # Start with one ingredient entry
        self.ingredient_entries = []
        self.add_ingredient_entry()

        # Add/Remove controls
        controls_frame = ttk.Frame(scrollable_frame, style="Modern.TFrame")
        controls_frame.pack(fill="x", pady=(8, 0))

        add_btn = ttk.Button(
            controls_frame,
            text="➕ Add Ingredient",
            style="Modern.TButton",
            command=self.add_ingredient_entry,
        )
        add_btn.pack(side="left", padx=(0, 8))

        remove_btn = ttk.Button(
            controls_frame,
            text="➖ Remove Ingredient",
            style="Secondary.TButton",
            command=self.remove_ingredient_entry,
        )
        remove_btn.pack(side="left")

        # Recipe selection for ingredients
        recipe_select_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        recipe_select_frame.pack(fill="x", pady=(16, 0))
        recipe_select_frame.configure(padding=12)

        recipe_select_label = ttk.Label(
            recipe_select_frame,
            text="Select Recipe (optional - defaults to last added)",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        recipe_select_label.pack(anchor="w", pady=(0, 8))

        self.recipe_combo = ttk.Combobox(
            recipe_select_frame, state="readonly", width=50
        )
        self.recipe_combo.pack(fill="x")
        self.populate_recipe_combo()

        # Form buttons
        button_frame = ttk.Frame(scrollable_frame, style="Modern.TFrame")
        button_frame.pack(fill="x", pady=(16, 0))

        save_btn = ttk.Button(
            button_frame,
            text="💾 Save Ingredients",
            style="Modern.TButton",
            command=self.save_ingredients,
        )
        save_btn.pack(side="left", padx=(0, 8))

        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Form",
            style="Secondary.TButton",
            command=self.clear_ingredients_form,
        )
        clear_btn.pack(side="left")

    def setup_import_recipe_tab(self):
        """Setup the tab for importing recipes from URLs."""
        self.tab_import_recipe.configure(padding=16)

        # Header
        header_frame = ttk.Frame(self.tab_import_recipe, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 16))

        form_header = ttk.Label(
            header_frame, text="Import Recipe from URL", style="Heading.TLabel"
        )
        form_header.pack(anchor="w")

        # URL input
        url_frame = ttk.Frame(self.tab_import_recipe, style="Card.TFrame")
        url_frame.pack(fill="x", pady=(0, 12))
        url_frame.configure(padding=12)

        self.url_entry = ModernEntry(
            url_frame,
            label_text="Recipe URL",
            placeholder="Enter recipe URL (e.g., https://15gram.be/...)",
        )
        self.url_entry.pack(fill="x")

        # Buttons and feedback
        button_feedback_frame = ttk.Frame(self.tab_import_recipe, style="Modern.TFrame")
        button_feedback_frame.pack(fill="x", pady=(16, 0))

        import_btn = ttk.Button(
            button_feedback_frame,
            text="🔗 Fetch & Add Recipe",
            style="Modern.TButton",
            command=self.import_recipe_from_url,
        )
        import_btn.pack(side="left", padx=(0, 8))

        self.import_feedback_label = ttk.Label(
            button_feedback_frame,
            text="",
            style="Card.TLabel",
            foreground=ModernTheme.COLORS["info"],
        )
        self.import_feedback_label.pack(side="left", padx=(8, 0))

    def import_recipe_from_url(self):
        """Fetch a recipe from a supported URL, parse, and add to the database."""
        from tkinter_gui.importers import import_recipe_from_url as importer_func

        importer_func(
            self.url_entry.get(),
            self.status_bar,
            self.import_feedback_label,
            self.db,
            self.refresh_recipe_list,
            self.populate_recipe_combo,
            self.url_entry.clear,
        )

    def add_ingredient_entry(self):
        """Add a new ingredient entry field"""
        index = len(self.ingredient_entries) + 1
        entry = ModernIngredientEntry(self.entries_frame, index)
        entry.pack(fill="x", pady=(0, 8))
        self.ingredient_entries.append(entry)

    def remove_ingredient_entry(self):
        """Remove the last ingredient entry field"""
        if len(self.ingredient_entries) > 1:
            entry = self.ingredient_entries.pop()
            entry.destroy()

    def setup_menu_bar(self):
        """Setup menu bar with help and options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Refresh All", command=self.refresh_all)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear Search", command=self.clear_search)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """
Keyboard Shortcuts:

Ctrl+N - Switch to Add Recipe tab
Ctrl+R - Refresh recipe list  
Ctrl+G - Generate week menu
Ctrl+E - Export menu
F5 - Refresh recipe list

Navigation:
Tab - Move between form fields
Enter - Submit forms
Escape - Cancel operations
        """

        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text.strip())

    def show_about(self):
        """Show about dialog"""
        about_text = """
CuisineCraft - Professional Recipe Manager

Version: 2.0 (Modern UI)
Created with Python and tkinter

Features:
• Modern, professional interface
• Recipe management with search
• Week menu generation  
• Shopping list creation
• Multiple export formats
• Keyboard shortcuts
        """

        messagebox.showinfo("About CuisineCraft", about_text.strip())

    def refresh_all(self):
        """Refresh all data"""
        self.refresh_recipe_list()
        self.populate_recipe_combo()
        self.status_bar.set_status("All data refreshed")

    def clear_search(self):
        """Clear search and show all recipes"""
        self.search_entry.clear()
        self.refresh_recipe_list()

    def save_recipe(self):
        """Save recipe to database with modern UX feedback"""
        self.status_bar.set_status("Saving recipe...", show_progress=True)

        try:
            # Convert cooking_time to integer (minutes)
            cooking_time_str = self.recipe_entries["cooking_time"].get().strip()
            cooking_time_int = parse_cooking_time(cooking_time_str)

            recipe = Recipe(
                name=self.recipe_entries["name"].get(),
                persons=int(self.recipe_entries["persons"].get() or 0),
                cooking_time=cooking_time_int,  # Now storing as integer
                cuisine_origin=self.recipe_entries["cuisine_origin"].get(),
                file_location=self.recipe_entries["file_location"].get(),
                url=self.recipe_entries["url"].get(),
                health_grade=int(self.recipe_entries["health_grade"].get() or 0),
            )

            with DatabaseHandler() as db:
                recipe_id = db.insert_recipe(recipe)

            # Show success message
            self.status_bar.set_status(f"Recipe saved successfully! ID: {recipe_id}")
            messagebox.showinfo("Success", "Recipe saved successfully!")
            self.clear_recipe_form()

            # Refresh recipe combo in ingredients tab
            self.populate_recipe_combo()

        except ValueError as e:
            self.status_bar.set_status("Validation error - please check inputs")
            messagebox.showerror(
                "Invalid Input",
                f"Please check your inputs: {str(e)}\n\nNumbers required for persons and health grade.",
            )
        except Exception as e:
            logger.error(f"Failed to save recipe: {str(e)}")
            self.status_bar.set_status(f"Error saving recipe: {str(e)}")
            messagebox.showerror("Error", f"Failed to save recipe: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def save_ingredients(self):
        """Save ingredients to database with modern UX feedback"""
        self.status_bar.set_status("Saving ingredients...", show_progress=True)

        ingredients = []
        for entry in self.ingredient_entries:
            ingredient = entry.get_ingredient()
            if ingredient:
                ingredients.append(ingredient)

        if not ingredients:
            self.status_bar.set_status("No ingredients entered")
            messagebox.showwarning(
                "No Ingredients", "Please enter at least one ingredient!"
            )
            return

        try:
            with DatabaseHandler() as db:
                # Get recipe ID from combo selection or use latest
                selected_recipe = self.recipe_combo.get()
                if selected_recipe:
                    recipe_id = int(selected_recipe.split(" - ")[0])
                else:
                    # Fall back to latest recipe
                    result = db.cursor.execute(
                        "SELECT ID FROM maaltijden ORDER BY rowid DESC LIMIT 1"
                    ).fetchone()

                    if not result:
                        self.status_bar.set_status(
                            "No recipes found to link ingredients to"
                        )
                        messagebox.showwarning(
                            "No Recipes",
                            "Please add a recipe first before adding ingredients!",
                        )
                        return

                    recipe_id = result[0]

                db.insert_ingredients(recipe_id, ingredients)

            # Show success message
            self.status_bar.set_status(f"Saved {len(ingredients)} ingredients")
            messagebox.showinfo("Success", "Ingredients saved successfully!")
            self.clear_ingredients_form()

        except Exception as e:
            logger.error(f"Failed to save ingredients: {str(e)}")
            self.status_bar.set_status(f"Error saving ingredients: {str(e)}")
            messagebox.showerror("Error", f"Failed to save ingredients: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def on_search_change(self, event=None):
        """Handle real-time search as user types"""
        # Add a small delay to avoid too frequent searches
        if hasattr(self, "_search_after_id"):
            self.root.after_cancel(self._search_after_id)
        self._search_after_id = self.root.after(300, self.search_recipes)

    def search_recipes(self):
        """Search recipes based on search term"""
        search_term = self.search_entry.get().strip().lower()

        if not search_term:
            self.refresh_recipe_list()
            return

        self.status_bar.set_status("Searching recipes...", show_progress=True)
        self.recipe_listbox.delete(0, "end")

        try:
            with DatabaseHandler() as db:
                # Search in recipe names, cuisine origin, and ingredients
                df = db.search_recipes(search_term)

                if df.empty:
                    self.recipe_listbox.insert(
                        tk.END, "No recipes found matching your search."
                    )
                    self.status_bar.set_status("No recipes found")
                else:
                    for idx, row in df.iterrows():
                        self.recipe_listbox.insert(
                            tk.END,
                            f"{row['ID']}) {row['recept_naam']} ({row['keuken_origine']})",
                        )
                    self.status_bar.set_status(f"Found {len(df)} recipes")

        except Exception as e:
            logger.error(f"Failed to search recipes: {str(e)}")
            self.status_bar.set_status(f"Search error: {str(e)}")
            messagebox.showerror("Search Error", f"Failed to search recipes: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def on_manual_menu_search_change(self, event=None):
        """Handle real-time search for manual week menu as user types"""
        if hasattr(self, "_manual_search_after_id"):
            self.root.after_cancel(self._manual_search_after_id)
        self._manual_search_after_id = self.root.after(
            300, self.refresh_manual_menu_recipe_list
        )

    def refresh_manual_menu_recipe_list(self):
        """Refresh recipe list for manual week menu with modern loading indicator"""
        self.status_bar.set_status(
            "Refreshing manual menu recipe list...", show_progress=True
        )
        self.manual_menu_recipe_listbox.delete(0, "end")

        search_term = self.manual_menu_search_entry.get().strip().lower()

        try:
            with DatabaseHandler() as db:
                if search_term:
                    df = db.search_recipes(search_term)
                else:
                    df = db.get_all_recipes()

                if df.empty:
                    self.manual_menu_recipe_listbox.insert(tk.END, "No recipes found.")
                    self.status_bar.set_status("No recipes found for manual menu")
                else:
                    for idx, row in df.iterrows():
                        self.manual_menu_recipe_listbox.insert(
                            tk.END,
                            f"{row['ID']}) {row['recept_naam']} ({row['keuken_origine']})",
                        )
                    self.status_bar.set_status(
                        f"Loaded {len(df)} recipes for manual menu"
                    )

        except Exception as e:
            logger.error(f"Failed to refresh manual menu recipe list: {str(e)}")
            self.status_bar.set_status(
                f"Error loading recipes for manual menu: {str(e)}"
            )
            messagebox.showerror(
                "Error", f"Failed to refresh manual menu recipe list: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def refresh_recipe_list(self):
        """Refresh recipe list with modern loading indicator"""
        self.status_bar.set_status("Refreshing recipe list...", show_progress=True)
        self.recipe_listbox.delete(0, "end")

        try:
            with DatabaseHandler() as db:
                df = db.get_all_recipes()

                for idx, row in df.iterrows():
                    self.recipe_listbox.insert(
                        tk.END,
                        f"{row['ID']}) {row['recept_naam']} ({row['keuken_origine']})",
                    )

            self.status_bar.set_status(f"Loaded {len(df)} recipes")

        except Exception as e:
            logger.error(f"Failed to refresh recipe list: {str(e)}")
            self.status_bar.set_status(f"Error loading recipes: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh recipe list: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def populate_manual_menu_combos(self):
        """Populate the comboboxes for manual week menu with available recipes."""
        try:
            with DatabaseHandler() as db:
                df = db.get_recipes_for_combo()
                # Store recipe ID and name for easy lookup
                self.all_recipes_for_manual_menu = {
                    row["ID"]: row["recept_naam"] for _, row in df.iterrows()
                }
                recipe_list_display = [
                    f"{row['ID']} - {row['recept_naam']}" for _, row in df.iterrows()
                ]

                for day in self.days_of_week:
                    combo = self.manual_week_menu_recipe_combos[day]
                    combo["values"] = recipe_list_display
                    # Ensure current selection is preserved if recipe still exists
                    current_recipe_id = self.week_menu_recipe_ids.get(day)
                    if (
                        current_recipe_id
                        and current_recipe_id in self.all_recipes_for_manual_menu
                    ):
                        combo.set(
                            f"{current_recipe_id} - {self.all_recipes_for_manual_menu[current_recipe_id]}"
                        )
                    else:
                        combo.set(
                            "Select a recipe"
                        )  # Reset if recipe not found or no selection

        except Exception as e:
            logger.error(f"Failed to populate manual menu combos: {str(e)}")
            self.status_bar.set_status(f"Error populating menu combos: {str(e)}")

    def on_manual_menu_recipe_select(self, event=None):
        """Handle selection from the manual menu recipe listbox."""
        selected_indices = self.manual_menu_recipe_listbox.curselection()
        if not selected_indices:
            return

        selected_item = self.manual_menu_recipe_listbox.get(selected_indices[0])
        # Extract ID and name: "ID) Name (Cuisine)"
        try:
            recipe_id_str = selected_item.split(")")[0]
            recipe_id = int(recipe_id_str)
            recipe_name = selected_item.split(") ")[1].split(" (")[0]

            # You could add logic here to automatically assign to a day,
            # or just make it available for manual assignment.
            # For now, we'll just log it or prepare for drag-and-drop (future)
            self.status_bar.set_status(
                f"Selected recipe: {recipe_name} (ID: {recipe_id})"
            )
        except Exception as e:
            logger.warning(f"Could not parse selected recipe: {selected_item} - {e}")

    def on_manual_menu_recipe_assign(self, day: str):
        """Handle recipe assignment to a specific day via combobox."""
        selected_value = self.week_menu_vars[day].get()
        if "Select a recipe" in selected_value or not selected_value:
            self.week_menu_recipe_ids[day] = None
            self.status_bar.set_status(f"Cleared recipe for {day}")
        else:
            try:
                recipe_id = int(selected_value.split(" - ")[0])
                self.week_menu_recipe_ids[day] = recipe_id
                self.status_bar.set_status(
                    f"Assigned {selected_value.split(' - ')[1]} to {day}"
                )
            except ValueError:
                self.week_menu_recipe_ids[day] = None
                self.status_bar.set_status(f"Invalid recipe selection for {day}")
        self.update_manual_menu_ingredients_list()

    def clear_day_recipe(self, day: str):
        """Clear the recipe assigned to a specific day."""
        self.week_menu_vars[day].set("Select a recipe")
        self.week_menu_recipe_ids[day] = None
        self.status_bar.set_status(f"Cleared recipe for {day}")
        self.update_manual_menu_ingredients_list()

    def save_manual_week_menu(self):
        """Save the current manual week menu to the database."""
        self.status_bar.set_status("Saving manual week menu...", show_progress=True)
        try:
            with DatabaseHandler() as db:
                # Clear existing menu before saving new one
                db.clear_week_menu()

                saved_count = 0
                for day, recipe_id in self.week_menu_recipe_ids.items():
                    if recipe_id is not None:
                        entry = WeekMenuEntry(day=day, recipe_id=recipe_id)
                        db.insert_week_menu_entry(entry)
                        saved_count += 1

            self.status_bar.set_status(
                f"Saved {saved_count} recipes to manual week menu."
            )
            messagebox.showinfo(
                "Success",
                f"Manual week menu saved successfully with {saved_count} entries!",
            )
        except Exception as e:
            logger.error(f"Failed to save manual week menu: {str(e)}")
            self.status_bar.set_status(f"Error saving manual week menu: {str(e)}")
            messagebox.showerror("Error", f"Failed to save manual week menu: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def load_manual_week_menu(self):
        """Load the latest saved manual week menu from the database."""
        self.status_bar.set_status(
            "Loading latest manual week menu...", show_progress=True
        )
        try:
            with DatabaseHandler() as db:
                latest_menu_data = db.get_latest_week_menu()

                # Reset current selections
                for day in self.days_of_week:
                    self.week_menu_vars[day].set("Select a recipe")
                    self.week_menu_recipe_ids[day] = None

                loaded_count = 0
                for entry in latest_menu_data:
                    if entry:  # Check if entry is not None (meaning a recipe was assigned for that day)
                        day = entry["day"]
                        recipe_id = entry["recipe_id"]
                        recipe_name = entry["recipe_name"]

                        if day in self.week_menu_vars:
                            self.week_menu_vars[day].set(f"{recipe_id} - {recipe_name}")
                            self.week_menu_recipe_ids[day] = recipe_id
                            loaded_count += 1

            self.status_bar.set_status(
                f"Loaded {loaded_count} recipes for manual week menu."
            )
            self.update_manual_menu_ingredients_list()  # Update shopping list based on loaded menu
        except Exception as e:
            logger.error(f"Failed to load manual week menu: {str(e)}")
            self.status_bar.set_status(f"Error loading manual week menu: {str(e)}")
            messagebox.showerror("Error", f"Failed to load manual week menu: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def clear_all_manual_menu_recipes(self):
        """Clear all recipes from the manual week menu and reset UI."""
        if messagebox.askyesno(
            "Clear Menu",
            "Are you sure you want to clear all recipes from the manual week menu? This will also clear it from the database.",
        ):
            try:
                with DatabaseHandler() as db:
                    db.clear_week_menu()  # Clear from database

                for day in self.days_of_week:
                    self.week_menu_vars[day].set("Select a recipe")
                    self.week_menu_recipe_ids[day] = None

                self.update_manual_menu_ingredients_list()
                self.status_bar.set_status("All manual week menu recipes cleared.")
                messagebox.showinfo("Cleared", "Manual week menu cleared successfully.")
            except Exception as e:
                logger.error(f"Failed to clear all manual week menu recipes: {str(e)}")
                self.status_bar.set_status(f"Error clearing menu: {str(e)}")
                messagebox.showerror(
                    "Error", f"Failed to clear manual week menu: {str(e)}"
                )

    def export_manual_week_menu(self):
        """Export the current manual week menu with modern file dialog."""
        try:
            meal_names = []
            for day in self.days_of_week:
                recipe_id = self.week_menu_recipe_ids.get(day)
                if recipe_id is not None:
                    recipe_name = self.all_recipes_for_manual_menu.get(recipe_id)
                    if recipe_name:
                        meal_names.append(recipe_name)

            if not meal_names:
                messagebox.showwarning(
                    "No Menu",
                    "Please assign recipes to days in the manual week menu first!",
                )
                return

            with DatabaseHandler() as db:
                meals_with_urls = db.get_week_menu_recipes_with_urls(meal_names)
                grouped_ingredients = db.get_grouped_ingredients_for_meals(meal_names)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*"),
                ],
                title="Export Manual Week Menu",
            )

            if not file_path:
                return

            self.status_bar.set_status(
                "Exporting manual week menu...", show_progress=True
            )

            file_extension = Path(file_path).suffix.lower()

            if file_extension == ".csv":
                export_to_csv(file_path, meals_with_urls, grouped_ingredients)
            else:
                export_to_text(file_path, meals_with_urls, grouped_ingredients)

            self.status_bar.set_status(f"Manual menu exported to {file_path}")
            messagebox.showinfo(
                "Export Complete",
                f"Manual week menu exported successfully to:\n{file_path}",
            )

        except Exception as e:
            logger.error(f"Failed to export manual week menu: {str(e)}")
            self.status_bar.set_status(f"Export failed: {str(e)}")
            messagebox.showerror(
                "Export Error", f"Failed to export manual week menu: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def update_manual_menu_ingredients_list(self):
        """Update ingredients list for the manual week menu based on assigned recipes."""
        meal_names = []
        for day in self.days_of_week:
            recipe_id = self.week_menu_recipe_ids.get(day)
            if recipe_id is not None:
                recipe_name = self.all_recipes_for_manual_menu.get(recipe_id)
                if recipe_name:
                    meal_names.append(recipe_name)

        try:
            with DatabaseHandler() as db:
                results = db.get_ingredients_for_meals(meal_names)
                receipt_items_df = db.get_all_receipt_items()

                for item in self.manual_menu_ingredients_tree.get_children():
                    self.manual_menu_ingredients_tree.delete(item)

                for i, (ingredient, amount, unit) in enumerate(results):
                    price, shop = self.find_ingredient_price(
                        ingredient, receipt_items_df
                    )
                    self.manual_menu_ingredients_tree.insert(
                        "",
                        "end",
                        values=(
                            ingredient,
                            amount,
                            unit,
                            f"{price:.2f}" if price else "",
                            shop,
                        ),
                    )

        except Exception as e:
            logger.error(f"Failed to update manual menu ingredients list: {str(e)}")
            self.status_bar.set_status(
                f"Error updating manual menu ingredients: {str(e)}"
            )
            messagebox.showerror(
                "Error", f"Failed to update manual menu ingredients list: {str(e)}"
            )

    def generate_week_menu(self):
        """Generate week menu with modern loading indicator"""
        self.status_bar.set_status("Generating week menu...", show_progress=True)

        try:
            with DatabaseHandler() as db:
                df = db.get_all_recipes()

                if len(df) < 7:
                    messagebox.showwarning(
                        "Not Enough Recipes",
                        "You need at least 7 recipes to generate a week menu!",
                    )
                    return

                random_meals = df.sample(n=7)
                self.week_menu_listbox.delete(0, tk.END)

                for idx, meal in enumerate(random_meals["recept_naam"], 1):
                    self.week_menu_listbox.insert(tk.END, f"{idx}) {meal}")

                self.update_ingredients_list(random_meals["recept_naam"].tolist())
                self.status_bar.set_status("Week menu generated successfully")

        except Exception as e:
            logger.error(f"Failed to generate week menu: {str(e)}")
            self.status_bar.set_status(f"Error generating menu: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate week menu: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def update_ingredients_list(self, meals):
        """Update ingredients list for week menu"""
        try:
            with DatabaseHandler() as db:
                results = db.get_ingredients_for_meals(meals)
                receipt_items_df = db.get_all_receipt_items()

                # Clear existing items
                for item in self.ingredients_tree.get_children():
                    self.ingredients_tree.delete(item)

                # Insert new data
                for i, (ingredient, amount, unit) in enumerate(results):
                    price, shop = self.find_ingredient_price(
                        ingredient, receipt_items_df
                    )
                    self.ingredients_tree.insert(
                        "",
                        "end",
                        values=(
                            ingredient,
                            amount,
                            unit,
                            f"{price:.2f}" if price else "",
                            shop,
                        ),
                    )

        except Exception as e:
            logger.error(f"Failed to update ingredients list: {str(e)}")
            self.status_bar.set_status(f"Error updating ingredients: {str(e)}")
            messagebox.showerror(
                "Error", f"Failed to update ingredients list: {str(e)}"
            )

    def remove_selected_menu_items(self):
        """Remove selected recipes from the week menu listbox and update shopping list."""
        selected_indices = self.week_menu_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(
                "No Selection", "Please select items to remove from the week menu."
            )
            return

        # Convert tuple of indices to a list and sort in reverse order
        # This is crucial to avoid issues with index shifting when deleting items
        indices_to_remove = sorted(list(selected_indices), reverse=True)

        for index in indices_to_remove:
            self.week_menu_listbox.delete(index)

        # Get remaining recipes and update the shopping list
        remaining_meals = [
            self.week_menu_listbox.get(i).split(") ")[1]
            for i in range(self.week_menu_listbox.size())
        ]
        self.update_ingredients_list(remaining_meals)
        self.status_bar.set_status(
            f"Removed {len(selected_indices)} items from week menu."
        )

    def find_ingredient_price(
        self, ingredient_name: str, receipt_items_df: pd.DataFrame
    ) -> tuple[Optional[float], Optional[str]]:
        """Find the price of an ingredient from receipt data."""
        if receipt_items_df.empty:
            return None, None

        # Simple search: case-insensitive substring matching
        # A more advanced implementation could use fuzzy matching
        for _, row in receipt_items_df.iterrows():
            if ingredient_name.lower() in row["item_name"].lower():
                return row["price"], row["shop"]
        return None, None

    def export_week_menu(self):
        """Export week menu with modern file dialog"""
        try:
            meal_names = [
                self.week_menu_listbox.get(i).split(") ", 1)[
                    -1
                ]  # Extract only the meal name
                for i in range(self.week_menu_listbox.size())
            ]

            if not meal_names:
                messagebox.showwarning("No Menu", "Please generate a week menu first!")
                return

            with DatabaseHandler() as db:
                meals_with_urls = db.get_week_menu_recipes_with_urls(meal_names)
                grouped_ingredients = db.get_grouped_ingredients_for_meals(meal_names)

            # Get file path for export
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*"),
                ],
                title="Export Week Menu",
            )

            if not file_path:
                return

            self.status_bar.set_status("Exporting week menu...", show_progress=True)

            # Determine export format
            file_extension = Path(file_path).suffix.lower()

            if file_extension == ".csv":
                export_to_csv(file_path, meals_with_urls, grouped_ingredients)
            else:
                export_to_text(file_path, meals_with_urls, grouped_ingredients)

            self.status_bar.set_status(f"Menu exported to {file_path}")
            messagebox.showinfo(
                "Export Complete", f"Week menu exported successfully to:\n{file_path}"
            )

        except Exception as e:
            logger.error(f"Failed to export week menu: {str(e)}")
            self.status_bar.set_status(f"Export failed: {str(e)}")
            messagebox.showerror(
                "Export Error", f"Failed to export week menu: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def populate_recipe_combo(self):
        """Populate the recipe combo box with available recipes"""
        try:
            with DatabaseHandler() as db:
                df = db.get_recipes_for_combo()
                recipe_list = [
                    f"{row['ID']} - {row['recept_naam']}" for _, row in df.iterrows()
                ]
                self.recipe_combo["values"] = recipe_list

                if recipe_list:
                    self.recipe_combo.current(0)  # Select the most recent recipe

        except Exception as e:
            logger.error(f"Failed to populate recipe combo: {str(e)}")

    def clear_recipe_form(self):
        """Clear all recipe form fields"""
        for entry in self.recipe_entries.values():
            entry.clear()
        self.status_bar.set_status("Recipe form cleared")

    def clear_ingredients_form(self):
        """Clear all ingredient form fields"""
        for entry in self.ingredient_entries:
            entry.clear()
        self.status_bar.set_status("Ingredients form cleared")

    def on_closing(self):
        """Handle application closing"""
        try:
            self.status_bar.set_status("Closing application...")
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error during application shutdown: {str(e)}")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better UX"""
        # Ctrl+N for new recipe
        self.root.bind(
            "<Control-n>", lambda e: self.notebook.select(self.tab_add_recipe)
        )

        # Ctrl+R for refresh
        self.root.bind("<Control-r>", lambda e: self.refresh_recipe_list())

        # Ctrl+G for generate menu
        self.root.bind("<Control-g>", lambda e: self.generate_week_menu())

        # Ctrl+E for export
        self.root.bind("<Control-e>", lambda e: self.export_week_menu())

        # F5 for refresh (alternative)
        self.root.bind("<F5>", lambda e: self.refresh_recipe_list())

    def run(self):
        """Start the application"""
        try:
            # Handle window closing
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Setup keyboard shortcuts
            self.setup_keyboard_shortcuts()

            # Center the window
            self.center_window()

            # Start the main loop
            self.status_bar.set_status(
                "CuisineCraft ready! Use Ctrl+N for new recipe, Ctrl+R to refresh"
            )
            self.root.mainloop()

        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            messagebox.showerror("Application Error", f"An error occurred: {str(e)}")

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_manual_week_menu_tab(self):
        """Setup the tab for manually creating a week menu."""
        self.tab_manual_week_menu.configure(padding=16)

        # Main layout: Left for recipe list, Right for day-by-day selection
        main_paned_window = ttk.Panedwindow(
            self.tab_manual_week_menu, orient=tk.HORIZONTAL
        )
        main_paned_window.pack(fill="both", expand=True)

        # Left Frame: Recipe List and Search
        left_frame = ttk.Frame(main_paned_window, style="Card.TFrame")
        left_frame.configure(padding=12)
        main_paned_window.add(left_frame, weight=1)

        search_label = ttk.Label(
            left_frame,
            text="Search Recipes",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        search_label.pack(anchor="w", pady=(0, 8))

        self.manual_menu_search_entry = ModernEntry(
            left_frame, placeholder="Search by name, cuisine, or ingredient..."
        )
        self.manual_menu_search_entry.pack(fill="x")
        self.manual_menu_search_entry.entry.bind(
            "<KeyRelease>", self.on_manual_menu_search_change
        )

        listbox_frame = ttk.Frame(left_frame, style="Card.TFrame")
        listbox_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.manual_menu_recipe_listbox = tk.Listbox(
            listbox_frame,
            font=ModernTheme.FONTS["body"],
            bg=ModernTheme.COLORS["surface"],
            fg=ModernTheme.COLORS["text_primary"],
            selectbackground=ModernTheme.COLORS["primary_light"],
            selectforeground=ModernTheme.COLORS["surface"],
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
        )

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.manual_menu_recipe_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.manual_menu_recipe_listbox.yview)
        self.manual_menu_recipe_listbox.pack(fill="both", expand=True)
        self.manual_menu_recipe_listbox.bind(
            "<<ListboxSelect>>", self.on_manual_menu_recipe_select
        )

        # Right Frame: Day-by-day recipe selection and shopping list
        right_frame = ttk.Frame(main_paned_window, style="Card.TFrame")
        right_frame.configure(padding=12)
        main_paned_window.add(right_frame, weight=2)

        # Week menu selection
        menu_selection_frame = ttk.Frame(right_frame, style="Card.TFrame")
        menu_selection_frame.pack(fill="x", pady=(0, 16))
        menu_selection_frame.configure(padding=12)

        menu_select_label = ttk.Label(
            menu_selection_frame,
            text="Assign Recipes to Days",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        menu_select_label.pack(anchor="w", pady=(0, 8))

        self.days_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        self.week_menu_vars = {
            day: tk.StringVar(value="Select a recipe") for day in self.days_of_week
        }
        self.week_menu_recipe_ids = {
            day: None for day in self.days_of_week
        }  # Store recipe IDs

        for day in self.days_of_week:
            day_frame = ttk.Frame(menu_selection_frame, style="Modern.TFrame")
            day_frame.pack(fill="x", pady=2)

            ttk.Label(day_frame, text=f"{day}:", style="Modern.TLabel", width=10).pack(
                side="left"
            )

            combo = ttk.Combobox(
                day_frame, textvariable=self.week_menu_vars[day], state="readonly"
            )
            combo.pack(side="left", fill="x", expand=True, padx=(0, 8))
            combo.bind(
                "<<ComboboxSelected>>",
                lambda event, d=day: self.on_manual_menu_recipe_assign(d),
            )
            self.manual_week_menu_recipe_combos[day] = combo

            clear_day_btn = ttk.Button(
                day_frame,
                text="Clear",
                style="Secondary.TButton",
                command=lambda d=day: self.clear_day_recipe(d),
            )
            clear_day_btn.pack(side="right")

        # Action buttons for manual menu
        button_frame = ttk.Frame(right_frame, style="Card.TFrame")
        button_frame.pack(fill="x", pady=(0, 16))
        button_frame.configure(padding=12)

        save_menu_btn = ttk.Button(
            button_frame,
            text="💾 Save Menu",
            style="Modern.TButton",
            command=self.save_manual_week_menu,
        )
        save_menu_btn.pack(side="left", padx=(0, 8))

        load_menu_btn = ttk.Button(
            button_frame,
            text="🔄 Load Latest",
            style="Secondary.TButton",
            command=self.load_manual_week_menu,
        )
        load_menu_btn.pack(side="left", padx=(0, 8))

        clear_all_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear All",
            style="Danger.TButton",
            command=self.clear_all_manual_menu_recipes,
        )
        clear_all_btn.pack(side="left", padx=(0, 8))

        export_manual_btn = ttk.Button(
            button_frame,
            text="📤 Export Menu",
            style="Secondary.TButton",
            command=self.export_manual_week_menu,
        )
        export_manual_btn.pack(side="left")

        # Shopping list section (reusing ingredients_tree from auto menu tab)
        ingredients_frame = ttk.Frame(right_frame, style="Card.TFrame")
        ingredients_frame.pack(fill="both", expand=True)
        ingredients_frame.configure(padding=12)

        ing_label = ttk.Label(
            ingredients_frame,
            text="Shopping List for Manual Menu",
            style="Card.TLabel",
            font=ModernTheme.FONTS["subheading"],
        )
        ing_label.pack(anchor="w", pady=(0, 8))

        tree_frame = ttk.Frame(ingredients_frame, style="Card.TFrame")
        tree_frame.pack(fill="both", expand=True)

        self.manual_menu_ingredients_tree = ttk.Treeview(
            tree_frame,
            columns=("ingredients", "amount", "unit", "price", "shop"),
            show="headings",
            style="Modern.Treeview",
        )

        self.manual_menu_ingredients_tree.heading("ingredients", text="Ingredient")
        self.manual_menu_ingredients_tree.heading("amount", text="Amount")
        self.manual_menu_ingredients_tree.heading("unit", text="Unit")
        self.manual_menu_ingredients_tree.heading("price", text="Est. Price")
        self.manual_menu_ingredients_tree.heading("shop", text="Shop")

        self.manual_menu_ingredients_tree.column("ingredients", width=200)
        self.manual_menu_ingredients_tree.column("amount", width=80)
        self.manual_menu_ingredients_tree.column("unit", width=80)
        self.manual_menu_ingredients_tree.column("price", width=80)
        self.manual_menu_ingredients_tree.column("shop", width=100)

        tree_scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.manual_menu_ingredients_tree.yview,
        )
        tree_scrollbar.pack(side="right", fill="y")
        self.manual_menu_ingredients_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.manual_menu_ingredients_tree.pack(fill="both", expand=True)

        # Initial population of recipe list and comboboxes
        self.refresh_manual_menu_recipe_list()
        self.populate_manual_menu_combos()
        self.load_manual_week_menu()  # Load any previously saved menu on startup

