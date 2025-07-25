"""
CuisineCraft GUI Layout Module
Handles the creation and arrangement of Tkinter widgets and frames.
"""

import tkinter as tk
from tkinter import ttk
import logging

from theme import ModernTheme, ToolTip
from widgets.modern_entry import ModernEntry
from constants import DAYS_OF_WEEK

logger = logging.getLogger('CuisineCraft')

class GUILayout:
    def __init__(self, root, notebook, main_frame, status_bar_instance, ingredient_entries_list, manual_week_menu_recipe_combos, recipe_entries_dict, recipe_combo_widget, week_menu_vars_dict, week_menu_recipe_ids_dict):
        self.root = root
        self.notebook = notebook
        self.main_frame = main_frame
        self.status_bar = status_bar_instance
        self.ingredient_entries = ingredient_entries_list
        self.manual_week_menu_recipe_combos = manual_week_menu_recipe_combos
        self.recipe_entries = recipe_entries_dict
        self.recipe_combo = recipe_combo_widget
        self.week_menu_vars = week_menu_vars_dict
        self.week_menu_recipe_ids = week_menu_recipe_ids_dict

        # These will be set by the main GUI class after setup
        self.recipe_listbox = None
        self.week_menu_listbox = None
        self.ingredients_tree = None
        self.manual_menu_search_entry = None
        self.manual_menu_recipe_listbox = None
        self.manual_menu_ingredients_tree = None
        self.url_entry = None
        self.import_feedback_label = None
        self.processing_label = None
        self.entries_frame = None # For ingredient entries

        self.tab_recipes = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.tab_week_menu = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.tab_manual_week_menu = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.tab_add_recipe = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.tab_ingredients = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.tab_import_recipe = ttk.Frame(self.notebook, style='Modern.TFrame')

    def setup_header(self):
        """Create modern header with title and branding"""
        header_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 16))
        
        title = ttk.Label(header_frame, text="CuisineCraft", 
                         style='Heading.TLabel', font=('Segoe UI', 24, 'bold'))
        title.pack(side='left')
        
        subtitle = ttk.Label(header_frame, text="Professional Recipe Manager", 
                           style='Modern.TLabel', font=ModernTheme.FONTS['body'])
        subtitle.pack(side='left', padx=(8, 0), pady=(8, 0))

    def setup_notebook_tabs(self):
        """Create modern tabbed interface and add tabs"""
        self.notebook.add(self.tab_recipes, text='📋 Recipe List')
        self.notebook.add(self.tab_week_menu, text='🎲 Auto Menu')
        self.notebook.add(self.tab_manual_week_menu, text='✍️ Manual Menu')
        self.notebook.add(self.tab_add_recipe, text='➕ Add Recipe')
        self.notebook.add(self.tab_ingredients, text='🥕 Add Ingredients')
        self.notebook.add(self.tab_import_recipe, text='🔗 Import Recipe')

    def setup_recipe_list_tab(self, on_search_change_cmd, refresh_recipe_list_cmd, search_recipes_cmd):
        """Modern recipe list with search and filters"""
        self.tab_recipes.configure(padding=16)
        
        search_frame = ttk.Frame(self.tab_recipes, style='Card.TFrame')
        search_frame.pack(fill='x', pady=(0, 16))
        search_frame.configure(padding=12)
        
        search_label = ttk.Label(search_frame, text="Search Recipes", 
                               style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        search_label.pack(anchor='w', pady=(0, 8))
        
        self.search_entry = ModernEntry(search_frame, placeholder="Search by name, cuisine, or ingredient...")
        self.search_entry.pack(fill='x')
        self.search_entry.entry.bind('<KeyRelease>', on_search_change_cmd)
        
        list_frame = ttk.Frame(self.tab_recipes, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True)
        list_frame.configure(padding=12)
        
        list_header = ttk.Label(list_frame, text="Your Recipes", 
                               style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        list_header.pack(anchor='w', pady=(0, 8))
        
        listbox_frame = ttk.Frame(list_frame, style='Card.TFrame')
        listbox_frame.pack(fill='both', expand=True, pady=(0, 12))
        
        self.recipe_listbox = tk.Listbox(listbox_frame, 
                                       font=ModernTheme.FONTS['body'],
                                       bg=ModernTheme.COLORS['surface'],
                                       fg=ModernTheme.COLORS['text_primary'],
                                       selectbackground=ModernTheme.COLORS['primary_light'],
                                       selectforeground=ModernTheme.COLORS['surface'],
                                       borderwidth=0,
                                       highlightthickness=0,
                                       activestyle='none')
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')
        self.recipe_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.recipe_listbox.yview)
        self.recipe_listbox.pack(fill='both', expand=True)
        
        button_frame = ttk.Frame(list_frame, style='Card.TFrame')
        button_frame.pack(fill='x')
        
        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh List", 
                               style='Modern.TButton', command=refresh_recipe_list_cmd)
        refresh_btn.pack(side='left', padx=(0, 8))
        ToolTip(refresh_btn, "Refresh the recipe list (Ctrl+R)")
        
        search_btn = ttk.Button(button_frame, text="🔍 Search", 
                               style='Secondary.TButton', command=search_recipes_cmd)
        search_btn.pack(side='left')
        ToolTip(search_btn, "Search recipes by name, cuisine, or ingredient")

    def setup_week_menu_tab(self, generate_week_menu_cmd, export_week_menu_cmd, remove_selected_menu_items_cmd):
        """Modern week menu generator with enhanced UI"""
        self.tab_week_menu.configure(padding=16)
        
        generator_frame = ttk.Frame(self.tab_week_menu, style='Card.TFrame')
        generator_frame.pack(fill='x', pady=(0, 16))
        generator_frame.configure(padding=12)
        
        gen_label = ttk.Label(generator_frame, text="Week Menu Generator", 
                            style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        gen_label.pack(anchor='w', pady=(0, 12))
        
        controls_frame = ttk.Frame(generator_frame, style='Card.TFrame')
        controls_frame.pack(fill='x', pady=(0, 12))
        
        generate_btn = ttk.Button(controls_frame, text="🎲 Generate Week Menu", 
                                style='Modern.TButton', command=generate_week_menu_cmd)
        generate_btn.pack(side='left', padx=(0, 8))
        ToolTip(generate_btn, "Generate a random 7-day menu (Ctrl+G)")
        
        export_btn = ttk.Button(controls_frame, text="📤 Export Menu",
                               style='Secondary.TButton', command=export_week_menu_cmd)
        export_btn.pack(side='left')
        ToolTip(export_btn, "Export menu and shopping list to file (Ctrl+E)")
        
        remove_selected_btn = ttk.Button(controls_frame, text="🗑️ Remove Selected",
                                       style='Danger.TButton', command=remove_selected_menu_items_cmd)
        remove_selected_btn.pack(side='left', padx=(8, 0))
        ToolTip(remove_selected_btn, "Remove selected recipes from the week menu")
        
        menu_frame = ttk.Frame(self.tab_week_menu, style='Card.TFrame')
        menu_frame.pack(fill='x', pady=(0, 16))
        menu_frame.configure(padding=12)
        
        menu_label = ttk.Label(menu_frame, text="This Week's Menu", 
                             style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        menu_label.pack(anchor='w', pady=(0, 8))
        
        self.week_menu_listbox = tk.Listbox(menu_frame,
                                          font=ModernTheme.FONTS['body'],
                                          bg=ModernTheme.COLORS['surface'],
                                          fg=ModernTheme.COLORS['text_primary'],
                                          selectbackground=ModernTheme.COLORS['primary_light'],
                                          borderwidth=0,
                                          highlightthickness=0,
                                          height=8)
        self.week_menu_listbox.pack(fill='x', pady=(0, 8))
        
        ingredients_frame = ttk.Frame(self.tab_week_menu, style='Card.TFrame')
        ingredients_frame.pack(fill='both', expand=True)
        ingredients_frame.configure(padding=12)
        
        ing_label = ttk.Label(ingredients_frame, text="Shopping List", 
                            style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        ing_label.pack(anchor='w', pady=(0, 8))
        
        tree_frame = ttk.Frame(ingredients_frame, style='Card.TFrame')
        tree_frame.pack(fill='both', expand=True)
        
        self.ingredients_tree = ttk.Treeview(tree_frame,
                                           columns=('ingredients', 'amount', 'unit', 'price', 'shop'),
                                           show='headings',
                                          style='Modern.Treeview')
        
        self.ingredients_tree.heading('ingredients', text='Ingredient')
        self.ingredients_tree.heading('amount', text='Amount')
        self.ingredients_tree.heading('unit', text='Unit')
        self.ingredients_tree.heading('price', text='Est. Price')
        self.ingredients_tree.heading('shop', text='Shop')
        
        self.ingredients_tree.column('ingredients', width=200)
        self.ingredients_tree.column('amount', width=80)
        self.ingredients_tree.column('unit', width=80)
        self.ingredients_tree.column('price', width=80)
        self.ingredients_tree.column('shop', width=100)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", 
                                     command=self.ingredients_tree.yview)
        tree_scrollbar.pack(side="right", fill="y")
        self.ingredients_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.ingredients_tree.pack(fill="both", expand=True)

    def setup_recipe_tab(self, save_recipe_cmd, clear_recipe_form_cmd):
        """Modern recipe addition form"""
        self.tab_add_recipe.configure(padding=16)
        
        canvas = tk.Canvas(self.tab_add_recipe, bg=ModernTheme.COLORS['background'], 
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_add_recipe, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        header_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 16))
        
        form_header = ttk.Label(header_frame, text="Add New Recipe", 
                               style='Heading.TLabel')
        form_header.pack(anchor='w')
        
        fields = [
            ("name", "Recipe Name", "Enter recipe name"),
            ("persons", "Number of Persons", "Enter number of persons"),
            ("cooking_time", "Cooking Time", "e.g., 30 minutes"),
            ("cuisine_origin", "Cuisine Origin", "e.g., Italian"),
            ("file_location", "File Location", "Path to recipe file"),
            ("url", "Recipe URL", "Optional recipe URL"),
            ("health_grade", "Health Grade (1-3, 1 being healthiest)", "1-3")
        ]
        
        for field, label, placeholder in fields:
            frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
            frame.pack(fill='x', pady=(0, 12))
            frame.configure(padding=12)
            
            entry = ModernEntry(frame, label_text=label, placeholder=placeholder, width=100)
            entry.pack(fill='x')
            self.recipe_entries[field] = entry
        
        button_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=(16, 0))
        
        save_btn = ttk.Button(button_frame, text="💾 Save Recipe", 
                            style='Modern.TButton', command=save_recipe_cmd)
        save_btn.pack(side='left', padx=(0, 8))
        
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Form", 
                             style='Secondary.TButton', command=clear_recipe_form_cmd)
        clear_btn.pack(side='left')

    def setup_ingredients_tab(self, add_ingredient_entry_cmd, remove_ingredient_entry_cmd, populate_recipe_combo_cmd, save_ingredients_cmd, clear_ingredients_form_cmd):
        """Modern ingredients form"""
        self.tab_ingredients.configure(padding=16)
        
        canvas = tk.Canvas(self.tab_ingredients, bg=ModernTheme.COLORS['background'], 
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_ingredients, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        header_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 16))
        
        header = ttk.Label(header_frame, text="Add Ingredients", 
                         style='Heading.TLabel')
        header.pack(anchor='w')
        
        instruction_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        instruction_frame.pack(fill='x', pady=(0, 16))
        instruction_frame.configure(padding=12)
        
        instructions = ttk.Label(instruction_frame, 
                               text="Enter ingredients with amount, unit, and name. Price is optional.",
                               style='Card.TLabel')
        instructions.pack(anchor='w')

        self.entries_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        self.entries_frame.pack(fill='x')

        # Initial ingredient entry will be added by the main GUI class
        # self.add_ingredient_entry() 

        controls_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        controls_frame.pack(fill='x', pady=(8, 0))

        add_btn = ttk.Button(controls_frame, text="➕ Add Ingredient",
                           style='Modern.TButton', command=add_ingredient_entry_cmd)
        add_btn.pack(side='left', padx=(0, 8))

        remove_btn = ttk.Button(controls_frame, text="➖ Remove Ingredient",
                              style='Secondary.TButton', command=remove_ingredient_entry_cmd)
        remove_btn.pack(side='left')

        recipe_select_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        recipe_select_frame.pack(fill='x', pady=(16, 0))
        recipe_select_frame.configure(padding=12)
        
        recipe_select_label = ttk.Label(recipe_select_frame, 
                                      text="Select Recipe (optional - defaults to last added)", 
                                      style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        recipe_select_label.pack(anchor='w', pady=(0, 8))
        
        self.recipe_combo = ttk.Combobox(recipe_select_frame, state="readonly", width=50)
        self.recipe_combo.pack(fill='x')
        populate_recipe_combo_cmd() # Populate on setup
        
        button_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=(16, 0))
        
        save_btn = ttk.Button(button_frame, text="💾 Save Ingredients", 
                            style='Modern.TButton', command=save_ingredients_cmd)
        save_btn.pack(side='left', padx=(0, 8))
        
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Form", 
                             style='Secondary.TButton', command=clear_ingredients_form_cmd)
        clear_btn.pack(side='left')

    def setup_import_recipe_tab(self, import_recipe_from_url_cmd):
        """Setup the tab for importing recipes from URLs."""
        self.tab_import_recipe.configure(padding=16)

        header_frame = ttk.Frame(self.tab_import_recipe, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 16))
        
        form_header = ttk.Label(header_frame, text="Import Recipe from URL",
                               style='Heading.TLabel')
        form_header.pack(anchor='w')

        url_frame = ttk.Frame(self.tab_import_recipe, style='Card.TFrame')
        url_frame.pack(fill='x', pady=(0, 12))
        url_frame.configure(padding=12)
        
        self.url_entry = ModernEntry(url_frame, label_text="Recipe URL",
                                     placeholder="Enter recipe URL (e.g., https://15gram.be/...)")
        self.url_entry.pack(fill='x')

        button_feedback_frame = ttk.Frame(self.tab_import_recipe, style='Modern.TFrame')
        button_feedback_frame.pack(fill='x', pady=(16, 0))

        import_btn = ttk.Button(button_feedback_frame, text="🔗 Fetch & Add Recipe",
                                style='Modern.TButton', command=import_recipe_from_url_cmd)
        import_btn.pack(side='left', padx=(0, 8))

        self.import_feedback_label = ttk.Label(button_feedback_frame, text="",
                                               style='Card.TLabel', foreground=ModernTheme.COLORS['info'])
        self.import_feedback_label.pack(side='left', padx=(8, 0))

    def setup_manual_week_menu_tab(self, on_manual_menu_search_change_cmd, on_manual_menu_recipe_select_cmd, on_manual_menu_recipe_assign_cmd, clear_day_recipe_cmd, save_manual_week_menu_cmd, load_manual_week_menu_cmd, clear_all_manual_menu_recipes_cmd, export_manual_week_menu_cmd, refresh_manual_menu_recipe_list_cmd, update_manual_menu_ingredients_list_cmd):
        """Setup the tab for manually creating a week menu."""
        self.tab_manual_week_menu.configure(padding=16)

        main_paned_window = ttk.Panedwindow(self.tab_manual_week_menu, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill='both', expand=True)

        left_frame = ttk.Frame(main_paned_window, style='Card.TFrame')
        left_frame.configure(padding=12)
        main_paned_window.add(left_frame, weight=1)

        search_label = ttk.Label(left_frame, text="Search Recipes",
                               style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        search_label.pack(anchor='w', pady=(0, 8))

        self.manual_menu_search_entry = ModernEntry(left_frame, placeholder="Search by name, cuisine, or ingredient...")
        self.manual_menu_search_entry.pack(fill='x')
        self.manual_menu_search_entry.entry.bind('<KeyRelease>', on_manual_menu_search_change_cmd)

        listbox_frame = ttk.Frame(left_frame, style='Card.TFrame')
        listbox_frame.pack(fill='both', expand=True, pady=(12, 0))

        self.manual_menu_recipe_listbox = tk.Listbox(listbox_frame,
                                                   font=ModernTheme.FONTS['body'],
                                                   bg=ModernTheme.COLORS['surface'],
                                                   fg=ModernTheme.COLORS['text_primary'],
                                                   selectbackground=ModernTheme.COLORS['primary_light'],
                                                   selectforeground=ModernTheme.COLORS['surface'],
                                                   borderwidth=0,
                                                   highlightthickness=0,
                                                   activestyle='none')

        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')
        self.manual_menu_recipe_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.manual_menu_recipe_listbox.yview)
        self.manual_menu_recipe_listbox.pack(fill='both', expand=True)
        self.manual_menu_recipe_listbox.bind('<<ListboxSelect>>', on_manual_menu_recipe_select_cmd)

        right_frame = ttk.Frame(main_paned_window, style='Card.TFrame')
        right_frame.configure(padding=12)
        main_paned_window.add(right_frame, weight=2)

        menu_selection_frame = ttk.Frame(right_frame, style='Card.TFrame')
        menu_selection_frame.pack(fill='x', pady=(0, 16))
        menu_selection_frame.configure(padding=12)

        menu_select_label = ttk.Label(menu_selection_frame, text="Assign Recipes to Days",
                                    style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        menu_select_label.pack(anchor='w', pady=(0, 8))

        for day in DAYS_OF_WEEK:
            day_frame = ttk.Frame(menu_selection_frame, style='Modern.TFrame')
            day_frame.pack(fill='x', pady=2)

            ttk.Label(day_frame, text=f"{day}:", style='Modern.TLabel', width=10).pack(side='left')
            
            combo = ttk.Combobox(day_frame, textvariable=self.week_menu_vars[day], state="readonly")
            combo.pack(side='left', fill='x', expand=True, padx=(0, 8))
            combo.bind("<<ComboboxSelected>>", lambda event, d=day: on_manual_menu_recipe_assign_cmd(d))
            self.manual_week_menu_recipe_combos[day] = combo

            clear_day_btn = ttk.Button(day_frame, text="Clear", style='Secondary.TButton',
                                       command=lambda d=day: clear_day_recipe_cmd(d))
            clear_day_btn.pack(side='right')

        button_frame = ttk.Frame(right_frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=(0, 16))
        button_frame.configure(padding=12)

        save_menu_btn = ttk.Button(button_frame, text="💾 Save Menu",
                                 style='Modern.TButton', command=save_manual_week_menu_cmd)
        save_menu_btn.pack(side='left', padx=(0, 8))

        load_menu_btn = ttk.Button(button_frame, text="🔄 Load Latest",
                                 style='Secondary.TButton', command=load_manual_week_menu_cmd)
        load_menu_btn.pack(side='left', padx=(0, 8))

        clear_all_btn = ttk.Button(button_frame, text="🗑️ Clear All",
                                 style='Danger.TButton', command=clear_all_manual_menu_recipes_cmd)
        clear_all_btn.pack(side='left', padx=(0, 8))

        export_manual_btn = ttk.Button(button_frame, text="📤 Export Menu",
                                     style='Secondary.TButton', command=export_manual_week_menu_cmd)
        export_manual_btn.pack(side='left')

        ingredients_frame = ttk.Frame(right_frame, style='Card.TFrame')
        ingredients_frame.pack(fill='both', expand=True)
        ingredients_frame.configure(padding=12)

        ing_label = ttk.Label(ingredients_frame, text="Shopping List for Manual Menu",
                            style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        ing_label.pack(anchor='w', pady=(0, 8))

        tree_frame = ttk.Frame(ingredients_frame, style='Card.TFrame')
        tree_frame.pack(fill='both', expand=True)

        self.manual_menu_ingredients_tree = ttk.Treeview(tree_frame,
                                                       columns=('ingredients', 'amount', 'unit', 'price', 'shop'),
                                                       show='headings',
                                                       style='Modern.Treeview')

        self.manual_menu_ingredients_tree.heading('ingredients', text='Ingredient')
        self.manual_menu_ingredients_tree.heading('amount', text='Amount')
        self.manual_menu_ingredients_tree.heading('unit', text='Unit')
        self.manual_menu_ingredients_tree.heading('price', text='Est. Price')
        self.manual_menu_ingredients_tree.heading('shop', text='Shop')

        self.manual_menu_ingredients_tree.column('ingredients', width=200)
        self.manual_menu_ingredients_tree.column('amount', width=80)
        self.manual_menu_ingredients_tree.column('unit', width=80)
        self.manual_menu_ingredients_tree.column('price', width=80)
        self.manual_menu_ingredients_tree.column('shop', width=100)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                     command=self.manual_menu_ingredients_tree.yview)
        tree_scrollbar.pack(side="right", fill="y")
        self.manual_menu_ingredients_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.manual_menu_ingredients_tree.pack(fill="both", expand=True)

        # Initial population of recipe list and comboboxes will be handled by main GUI
        # self.refresh_manual_menu_recipe_list()
        # self.populate_manual_menu_combos()
        # self.load_manual_week_menu()