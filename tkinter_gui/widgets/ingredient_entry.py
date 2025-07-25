"""
Modern Ingredient Entry Widget
Specialized widget for ingredient input
"""

import tkinter as tk
from tkinter import ttk
from tkinter_gui.theme import ModernTheme
from tkinter_gui.models import Ingredient

class ModernIngredientEntry(ttk.Frame):
    """Modern ingredient entry with individual fields"""
    
    def __init__(self, parent, index: int):
        super().__init__(parent, style='Card.TFrame')
        self.index = index
        
        # Configure frame
        self.configure(padding=12)
        
        # Header
        header = ttk.Label(self, text=f"Ingredient {index}", 
                         style='Card.TLabel', font=ModernTheme.FONTS['subheading'])
        header.grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 8))
        
        # Amount
        self.amount_entry = ttk.Entry(self, width=8)
        self.amount_entry.grid(row=1, column=0, padx=(0, 8), sticky='ew')
        ttk.Label(self, text="Amount", style='Card.TLabel').grid(row=2, column=0, sticky='w')
        
        # Unit
        self.unit_entry = ttk.Entry(self, width=8)
        self.unit_entry.grid(row=1, column=1, padx=(0, 8), sticky='ew')
        ttk.Label(self, text="Unit", style='Card.TLabel').grid(row=2, column=1, sticky='w')
        
        # Ingredient name
        self.name_entry = ttk.Entry(self, width=20)
        self.name_entry.grid(row=1, column=2, padx=(0, 8), sticky='ew')
        ttk.Label(self, text="Ingredient", style='Card.TLabel').grid(row=2, column=2, sticky='w')
        
        # Price (optional)
        self.price_entry = ttk.Entry(self, width=8)
        self.price_entry.grid(row=1, column=3, sticky='ew')
        ttk.Label(self, text="Price (optional)", style='Card.TLabel').grid(row=2, column=3, sticky='w')
        
        # Configure column weights
        self.columnconfigure(2, weight=1)
    
    def get_ingredient(self) -> Ingredient:
        """Extract ingredient from entry fields"""
        amount = self.amount_entry.get().strip()
        unit = self.unit_entry.get().strip()
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        
        if not amount or not name:
            return None
            
        try:
            return Ingredient(
                amount=float(amount) if amount else 0,
                unit=unit,
                name=name,
                price=float(price) if price else 0.0
            )
        except ValueError:
            return None
    
    def clear(self):
        """Clear all entry fields"""
        self.amount_entry.delete(0, tk.END)
        self.unit_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
