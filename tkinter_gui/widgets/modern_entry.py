"""
Modern Entry Widget
Custom styled entry with validation and placeholder support
"""

import tkinter as tk
from tkinter import ttk
from tkinter_gui.theme import ModernTheme

class ModernEntry(ttk.Frame):
    """Modern styled entry widget with label and validation"""
    
    def __init__(self, parent, label_text="", placeholder="", validate_func=None, **kwargs):
        super().__init__(parent, style='Modern.TFrame')
        
        self.validate_func = validate_func
        self.error_var = tk.StringVar()
        
        # Label
        if label_text:
            self.label = ttk.Label(self, text=label_text, style='Modern.TLabel', 
                                 font=ModernTheme.FONTS['body'])
            self.label.pack(anchor='w', pady=(0, 4))
        
        # Entry frame for border effect
        self.entry_frame = ttk.Frame(self, style='Modern.TFrame')
        self.entry_frame.pack(fill='x', pady=(0, 2))
        
        # Entry widget
        self.entry = ttk.Entry(self.entry_frame, style='Modern.TEntry', 
                              font=ModernTheme.FONTS['body'], **kwargs)
        self.entry.pack(fill='x', padx=1, pady=1)
        
        # Placeholder
        if placeholder:
            self.placeholder = placeholder
            self.entry.insert(0, placeholder)
            self.entry.configure(foreground='gray')
            self.entry.bind('<FocusIn>', self._on_focus_in)
            self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Error label
        self.error_label = ttk.Label(self, textvariable=self.error_var, 
                                   style='Modern.TLabel', font=ModernTheme.FONTS['small'])
        self.error_label.configure(foreground=ModernTheme.COLORS['danger'])
        
        # Validation
        if validate_func:
            self.entry.bind('<KeyRelease>', self._validate)
    
    def _on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(foreground=ModernTheme.COLORS['text_primary'])
    
    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(foreground='gray')
    
    def _validate(self, event=None):
        if self.validate_func:
            value = self.get()
            if value and value != getattr(self, 'placeholder', ''):
                error = self.validate_func(value)
                if error:
                    self.error_var.set(error)
                    self.error_label.pack(anchor='w')
                else:
                    self.error_var.set('')
                    self.error_label.pack_forget()
    
    def get(self):
        value = self.entry.get()
        if hasattr(self, 'placeholder') and value == self.placeholder:
            return ''
        return value
    
    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        if hasattr(self, 'placeholder'):
            self.entry.configure(foreground=ModernTheme.COLORS['text_primary'])
    
    def clear(self):
        self.entry.delete(0, tk.END)
        if hasattr(self, 'placeholder'):
            self.entry.insert(0, self.placeholder)
            self.entry.configure(foreground='gray')
