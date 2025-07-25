"""
CuisineCraft GUI Event Handlers Module
Contains methods that respond to user interactions and update the GUI/database.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import logging
import pandas as pd
import datetime
import os

from db import DatabaseHandler
from models import Recipe, Ingredient, ReceiptItem, WeekMenuEntry
from utils import parse_cooking_time, export_to_text, export_to_csv
from ocr_utils import perform_ocr, parse_receipt, find_ingredient_price
from importers import import_recipe_from_url
from constants import DAYS_OF_WEEK

logger = logging.getLogger('CuisineCraft')

class GUIEventHandler:
    def __init__(self, gui_instance, db_handler, status_bar_instance, recipe_entries_dict, ingredient_entries_list, recipe_combo_widget, search_entry_widget, recipe_listbox_widget, week_menu_listbox_widget, ingredients_tree_widget, receipt_tree_widget, manual_menu_search_entry_widget, manual_menu_recipe_listbox_widget, manual_menu_ingredients_tree_widget, url_entry_widget, import_feedback_label_widget, processing_label_widget, notebook_widget, tab_add_recipe_widget, week_menu_vars_dict, week_menu_recipe_ids_dict):
        self.gui = gui_instance
        self.db = db_handler
        self.status_bar = status_bar_instance
        self.recipe_entries = recipe_entries_dict
        self.ingredient_entries = ingredient_entries_list
        self.recipe_combo = recipe_combo_widget
        self.search_entry = search_entry_widget
        self.recipe_listbox = recipe_listbox_widget
        self.week_menu_listbox = week_menu_listbox_widget
        self.ingredients_tree = ingredients_tree_widget
        self.receipt_tree = receipt_tree_widget
        self.manual_menu_search_entry = manual_menu_search_entry_widget
        self.manual_menu_recipe_listbox = manual_menu_recipe_listbox_widget
        self.manual_menu_ingredients_tree = manual_menu_ingredients_tree_widget
        self.url_entry = url_entry_widget
        self.import_feedback_label = import_feedback_label_widget
        self.processing_label = processing_label_widget
        self.notebook = notebook_widget
        self.tab_add_recipe = tab_add_recipe_widget
        self.week_menu_vars = week_menu_vars_dict
        self.week_menu_recipe_ids = week_menu_recipe_ids_dict

        self.current_receipt_shop = 'Unknown Shop'
        self.current_receipt_date = datetime.date.today().strftime('%Y-%m-%d')
        self.all_recipes_for_manual_menu = {} # To be populated by GUI

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
        self.gui.refresh_recipe_list() # Call method on main GUI instance
        self.gui.populate_recipe_combo() # Call method on main GUI instance
        self.status_bar.set_status("All data refreshed")

    def clear_search(self):
        """Clear search and show all recipes"""
        self.search_entry.clear()
        self.gui.refresh_recipe_list() # Call method on main GUI instance

    def save_recipe(self):
        """Save recipe to database with modern UX feedback"""
        self.status_bar.set_status("Saving recipe...", show_progress=True)
        
        try:
            cooking_time_str = self.recipe_entries["cooking_time"].get().strip()
            cooking_time_int = parse_cooking_time(cooking_time_str)
            
            recipe = Recipe(
                name=self.recipe_entries["name"].get(),
                persons=int(self.recipe_entries["persons"].get() or 0),
                cooking_time=cooking_time_int,
                cuisine_origin=self.recipe_entries["cuisine_origin"].get(),
                file_location=self.recipe_entries["file_location"].get(),
                url=self.recipe_entries["url"].get(),
                health_grade=int(self.recipe_entries["health_grade"].get() or 0)
            )
            
            with self.db() as db:
                recipe_id = db.insert_recipe(recipe)
            
            self.status_bar.set_status(f"Recipe saved successfully! ID: {recipe_id}")
            messagebox.showinfo("Success", "Recipe saved successfully!")
            self.gui.clear_recipe_form() # Call method on main GUI instance
            
            self.gui.populate_recipe_combo() # Call method on main GUI instance
            
        except ValueError as e:
            self.status_bar.set_status("Validation error - please check inputs")
            messagebox.showerror(
                "Invalid Input",
                f"Please check your inputs: {str(e)}\n\nNumbers required for persons and health grade."
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
                "No Ingredients",
                "Please enter at least one ingredient!"
            )
            return
        
        try:
            with self.db() as db:
                selected_recipe = self.recipe_combo.get()
                if selected_recipe:
                    recipe_id = int(selected_recipe.split(' - ')[0])
                else:
                    result = db.cursor.execute(
                        'SELECT ID FROM maaltijden ORDER BY rowid DESC LIMIT 1'
                    ).fetchone()
                    
                    if not result:
                        self.status_bar.set_status("No recipes found to link ingredients to")
                        messagebox.showwarning(
                            "No Recipes",
                            "Please add a recipe first before adding ingredients!"
                        )
                        return
                    
                    recipe_id = result[0]
                
                db.insert_ingredients(recipe_id, ingredients)
            
            self.status_bar.set_status(f"Saved {len(ingredients)} ingredients")
            messagebox.showinfo("Success", "Ingredients saved successfully!")
            self.gui.clear_ingredients_form() # Call method on main GUI instance
            
        except Exception as e:
            logger.error(f"Failed to save ingredients: {str(e)}")
            self.status_bar.set_status(f"Error saving ingredients: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Failed to save ingredients: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def on_search_change(self, event=None):
        """Handle real-time search as user types"""
        if hasattr(self.gui.root, '_search_after_id'):
            self.gui.root.after_cancel(self.gui.root._search_after_id)
        self.gui.root._search_after_id = self.gui.root.after(300, self.search_recipes)

    def search_recipes(self):
        """Search recipes based on search term"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.gui.refresh_recipe_list() # Call method on main GUI instance
            return
        
        self.status_bar.set_status("Searching recipes...", show_progress=True)
        self.recipe_listbox.delete(0, "end")
        
        try:
            with self.db() as db:
                df = db.search_recipes(search_term)
                
                if df.empty:
                    self.recipe_listbox.insert(tk.END, "No recipes found matching your search.")
                    self.status_bar.set_status("No recipes found")
                else:
                    for idx, row in df.iterrows():
                        self.recipe_listbox.insert(
                            tk.END,
                            f"{row['ID']}) {row['recept_naam']} ({row['keuken_origine']})"
                        )
                    self.status_bar.set_status(f"Found {len(df)} recipes")
                    
        except Exception as e:
            logger.error(f"Failed to search recipes: {str(e)}")
            self.status_bar.set_status(f"Search error: {str(e)}")
            messagebox.showerror(
                "Search Error",
                f"Failed to search recipes: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def on_manual_menu_search_change(self, event=None):
        """Handle real-time search for manual week menu as user types"""
        if hasattr(self.gui.root, '_manual_search_after_id'):
            self.gui.root.after_cancel(self.gui.root._manual_search_after_id)
        self.gui.root._manual_search_after_id = self.gui.root.after(300, self.gui.refresh_manual_menu_recipe_list) # Call method on main GUI instance

    def on_manual_menu_recipe_select(self, event=None):
        """Handle selection from the manual menu recipe listbox."""
        selected_indices = self.manual_menu_recipe_listbox.curselection()
        if not selected_indices:
            return

        selected_item = self.manual_menu_recipe_listbox.get(selected_indices[0])
        try:
            recipe_id_str = selected_item.split(')')[0]
            recipe_id = int(recipe_id_str)
            recipe_name = selected_item.split(') ')[1].split(' (')[0]
            
            self.status_bar.set_status(f"Selected recipe: {recipe_name} (ID: {recipe_id})")
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
                recipe_id = int(selected_value.split(' - ')[0])
                self.week_menu_recipe_ids[day] = recipe_id
                self.status_bar.set_status(f"Assigned {selected_value.split(' - ')[1]} to {day}")
            except ValueError:
                self.week_menu_recipe_ids[day] = None
                self.status_bar.set_status(f"Invalid recipe selection for {day}")
        self.gui.update_manual_menu_ingredients_list() # Call method on main GUI instance

    def clear_day_recipe(self, day: str):
        """Clear the recipe assigned to a specific day."""
        self.week_menu_vars[day].set("Select a recipe")
        self.week_menu_recipe_ids[day] = None
        self.status_bar.set_status(f"Cleared recipe for {day}")
        self.gui.update_manual_menu_ingredients_list() # Call method on main GUI instance

    def save_manual_week_menu(self):
        """Save the current manual week menu to the database."""
        self.status_bar.set_status("Saving manual week menu...", show_progress=True)
        try:
            with self.db() as db:
                db.clear_week_menu()
                
                saved_count = 0
                for day, recipe_id in self.week_menu_recipe_ids.items():
                    if recipe_id is not None:
                        entry = WeekMenuEntry(day=day, recipe_id=recipe_id)
                        db.insert_week_menu_entry(entry)
                        saved_count += 1
            
            self.status_bar.set_status(f"Saved {saved_count} recipes to manual week menu.")
            messagebox.showinfo("Success", f"Manual week menu saved successfully with {saved_count} entries!")
        except Exception as e:
            logger.error(f"Failed to save manual week menu: {str(e)}")
            self.status_bar.set_status(f"Error saving manual week menu: {str(e)}")
            messagebox.showerror("Error", f"Failed to save manual week menu: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def load_manual_week_menu(self):
        """Load the latest saved manual week menu from the database."""
        self.status_bar.set_status("Loading latest manual week menu...", show_progress=True)
        try:
            with self.db() as db:
                latest_menu_data = db.get_latest_week_menu()
                
                for day in DAYS_OF_WEEK:
                    self.week_menu_vars[day].set("Select a recipe")
                    self.week_menu_recipe_ids[day] = None

                loaded_count = 0
                for entry in latest_menu_data:
                    if entry:
                        day = entry['day']
                        recipe_id = entry['recipe_id']
                        recipe_name = entry['recipe_name']
                        
                        if day in self.week_menu_vars:
                            self.week_menu_vars[day].set(f"{recipe_id} - {recipe_name}")
                            self.week_menu_recipe_ids[day] = recipe_id
                            loaded_count += 1
            
            self.status_bar.set_status(f"Loaded {loaded_count} recipes for manual week menu.")
            self.gui.update_manual_menu_ingredients_list() # Call method on main GUI instance
        except Exception as e:
            logger.error(f"Failed to load manual week menu: {str(e)}")
            self.status_bar.set_status(f"Error loading manual week menu: {str(e)}")
            messagebox.showerror("Error", f"Failed to load manual week menu: {str(e)}")
        finally:
            self.status_bar.set_status("Ready")

    def clear_all_manual_menu_recipes(self):
        """Clear all recipes from the manual week menu and reset UI."""
        if messagebox.askyesno("Clear Menu", "Are you sure you want to clear all recipes from the manual week menu? This will also clear it from the database."):
            try:
                with self.db() as db:
                    db.clear_week_menu()
                
                for day in DAYS_OF_WEEK:
                    self.week_menu_vars[day].set("Select a recipe")
                    self.week_menu_recipe_ids[day] = None
                
                self.gui.update_manual_menu_ingredients_list() # Call method on main GUI instance
                self.status_bar.set_status("All manual week menu recipes cleared.")
                messagebox.showinfo("Cleared", "Manual week menu cleared successfully.")
            except Exception as e:
                logger.error(f"Failed to clear all manual week menu recipes: {str(e)}")
                self.status_bar.set_status(f"Error clearing menu: {str(e)}")
                messagebox.showerror("Error", f"Failed to clear manual week menu: {str(e)}")

    def export_manual_week_menu(self):
        """Export the current manual week menu with modern file dialog."""
        try:
            meal_names = []
            for day in DAYS_OF_WEEK:
                recipe_id = self.week_menu_recipe_ids.get(day)
                if recipe_id is not None:
                    recipe_name = self.gui.all_recipes_for_manual_menu.get(recipe_id) # Access from GUI instance
                    if recipe_name:
                        meal_names.append(recipe_name)

            if not meal_names:
                messagebox.showwarning(
                    "No Menu",
                    "Please assign recipes to days in the manual week menu first!"
                )
                return

            with self.db() as db:
                meals_with_urls = db.get_week_menu_recipes_with_urls(meal_names)
                grouped_ingredients = db.get_grouped_ingredients_for_meals(meal_names)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ],
                title="Export Manual Week Menu"
            )
            
            if not file_path:
                return
            
            self.status_bar.set_status("Exporting manual week menu...", show_progress=True)
            
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                export_to_csv(file_path, meals_with_urls, grouped_ingredients)
            else:
                export_to_text(file_path, meals_with_urls, grouped_ingredients)
            
            self.status_bar.set_status(f"Manual menu exported to {file_path}")
            messagebox.showinfo(
                "Export Complete",
                f"Manual week menu exported successfully to:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to export manual week menu: {str(e)}")
            self.status_bar.set_status(f"Export failed: {str(e)}")
            messagebox.showerror(
                "Export Error",
                f"Failed to export manual week menu: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def generate_week_menu(self):
        """Generate week menu with modern loading indicator"""
        self.status_bar.set_status("Generating week menu...", show_progress=True)
        
        try:
            with self.db() as db:
                df = db.get_all_recipes()
                
                if len(df) < 7:
                    messagebox.showwarning(
                        "Not Enough Recipes",
                        "You need at least 7 recipes to generate a week menu!"
                    )
                    return
                
                random_meals = df.sample(n=7)
                self.week_menu_listbox.delete(0, tk.END)
                
                for idx, meal in enumerate(random_meals['recept_naam'], 1):
                    self.week_menu_listbox.insert(
                        tk.END,
                        f"{idx}) {meal}"
                    )
                
                self.update_ingredients_list(random_meals['recept_naam'].tolist())
                self.status_bar.set_status("Week menu generated successfully")
                
        except Exception as e:
            logger.error(f"Failed to generate week menu: {str(e)}")
            self.status_bar.set_status(f"Error generating menu: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Failed to generate week menu: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def update_ingredients_list(self, meals):
        """Update ingredients list for week menu"""
        try:
            with self.db() as db:
                results = db.get_ingredients_for_meals(meals)
                receipt_items_df = db.get_all_receipt_items()
                
                for item in self.ingredients_tree.get_children():
                    self.ingredients_tree.delete(item)
                
                for i, (ingredient, amount, unit) in enumerate(results):
                    price, shop = find_ingredient_price(ingredient, receipt_items_df)
                    self.ingredients_tree.insert(
                        '',
                        'end',
                        values=(ingredient, amount, unit, f"{price:.2f}" if price else "", shop)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to update ingredients list: {str(e)}")
            self.status_bar.set_status(f"Error updating ingredients: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Failed to update ingredients list: {str(e)}"
            )

    def remove_selected_menu_items(self):
        """Remove selected recipes from the week menu listbox and update shopping list."""
        selected_indices = self.week_menu_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select items to remove from the week menu.")
            return

        indices_to_remove = sorted(list(selected_indices), reverse=True)

        for index in indices_to_remove:
            self.week_menu_listbox.delete(index)
        
        remaining_meals = [self.week_menu_listbox.get(i).split(') ')[1] for i in range(self.week_menu_listbox.size())]
        self.update_ingredients_list(remaining_meals)
        self.status_bar.set_status(f"Removed {len(selected_indices)} items from week menu.")

    def export_week_menu(self):
        """Export week menu with modern file dialog"""
        from pathlib import Path # Import here to avoid circular dependency if gui imports events
        try:
            meal_names = [
                self.week_menu_listbox.get(i).split(') ', 1)[-1]
                for i in range(self.week_menu_listbox.size())
            ]

            if not meal_names:
                messagebox.showwarning(
                    "No Menu",
                    "Please generate a week menu first!"
                )
                return

            with self.db() as db:
                meals_with_urls = db.get_week_menu_recipes_with_urls(meal_names)
                grouped_ingredients = db.get_grouped_ingredients_for_meals(meal_names)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ],
                title="Export Week Menu"
            )
            
            if not file_path:
                return
            
            self.status_bar.set_status("Exporting week menu...", show_progress=True)
            
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                export_to_csv(file_path, meals_with_urls, grouped_ingredients)
            else:
                export_to_text(file_path, meals_with_urls, grouped_ingredients)
            
            self.status_bar.set_status(f"Menu exported to {file_path}")
            messagebox.showinfo(
                "Export Complete",
                f"Week menu exported successfully to:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to export week menu: {str(e)}")
            self.status_bar.set_status(f"Export failed: {str(e)}")
            messagebox.showerror(
                "Export Error",
                f"Failed to export week menu: {str(e)}"
            )
        finally:
            self.status_bar.set_status("Ready")

    def upload_receipt(self):
        """Handle receipt image upload and OCR processing"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if not file_path:
            logger.info("Receipt upload cancelled by user.")
            return

        self.processing_label.config(text="Processing...")
        self.gui.root.update_idletasks() # Update GUI from main instance
        self.status_bar.set_status("Processing receipt...", show_progress=True)
        logger.info(f"Starting OCR processing for receipt: {file_path}")
        try:
            extracted_text = perform_ocr(file_path)
            
            messagebox.showinfo("Extracted Text", extracted_text)
            
            parsed_items, shop, price_date = parse_receipt(extracted_text)

            self.current_receipt_shop = shop
            self.current_receipt_date = price_date

            for item in self.receipt_tree.get_children():
                self.receipt_tree.delete(item)

            for item in parsed_items:
                self.receipt_tree.insert('', 'end', values=(
                    item.item_name, item.price, item.quantity, item.unit
                ))
            
            self.status_bar.set_status(f"Processed {len(parsed_items)} items from receipt.")
            logger.info(f"Successfully processed {len(parsed_items)} items from receipt.")

        except Exception as e:
            logger.error(f"Failed to process receipt: {str(e)}")
            self.status_bar.set_status(f"Error processing receipt: {str(e)}")
            messagebox.showerror("Receipt Processing Error", f"Failed to process receipt: {str(e)}")
        finally:
            self.processing_label.config(text="")
            self.status_bar.set_status("Ready")

    def save_receipt_items(self):
        """Save the items from the receipt tree to the database"""
        items_to_save = []
        shop = getattr(self, 'current_receipt_shop', 'Unknown Shop')
        price_date = getattr(self, 'current_receipt_date', datetime.date.today().strftime('%Y-%m-%d'))

        for child in self.receipt_tree.get_children():
            values = self.receipt_tree.item(child)['values']
            item = ReceiptItem(
                item_name=values[0],
                price=float(values[1]),
                quantity=float(values[2]) if values[2] else 1.0,
                unit=values[3],
                shop=shop,
                price_date=price_date
            )
            items_to_save.append(item)

        if not items_to_save:
            messagebox.showwarning("No Items", "No items to save.")
            return

        try:
            with self.db() as db:
                db.insert_receipt_items(items_to_save)
            
            messagebox.showinfo("Success", f"Successfully saved {len(items_to_save)} items.")
            for item in self.receipt_tree.get_children():
                self.receipt_tree.delete(item)

        except Exception as e:
            logger.error(f"Failed to save receipt items: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to save receipt items: {str(e)}")

    def import_recipe_from_url_event(self):
        """Wrapper for import_recipe_from_url to pass GUI elements."""
        import_recipe_from_url(
            self.url_entry.get(),
            self.status_bar,
            self.import_feedback_label,
            self.db,
            self.gui.refresh_recipe_list,
            self.gui.populate_recipe_combo,
            self.url_entry.clear
        )