"""
CuisineCraft Theme and UI Components
ModernTheme, ToolTip, and StatusBar implementations
"""

import tkinter as tk
from tkinter import ttk

class ToolTip:
    """Simple tooltip widget for better UX"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, 
                        background=ModernTheme.COLORS['secondary'],
                        foreground=ModernTheme.COLORS['surface'],
                        font=ModernTheme.FONTS['small'],
                        relief='solid', borderwidth=1, padx=4, pady=2)
        label.pack()
    
    def on_leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ModernTheme:
    """Modern theme manager with professional color scheme"""
    
    # Color palette
    COLORS = {
        'primary': '#314095',
        'primary_light': '#2b3882',
        'primary_dark': '#253070',
        'secondary': '#1f285d',
        'accent': '#19204b',
        'background': '#f8f9fa',
        'surface': '#ffffff',
        'text_primary': '#121838',
        'text_secondary': '#0c1025',
        'border': '#e0e6ed',
        'hover': '#eef2f7',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8'
    }
    
    # Fonts
    FONTS = {
        'heading': ('Segoe UI', 16, 'bold'),
        'subheading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'button': ('Segoe UI', 10, 'bold')
    }
    
    @classmethod
    def configure_style(cls, root):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        
        # Configure notebook (tabs)
        style.theme_use('clam')
        
        style.configure('Modern.TNotebook', 
                       background=cls.COLORS['background'],
                       borderwidth=0)
        
        style.configure('Modern.TNotebook.Tab',
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       padding=[20, 12],
                       borderwidth=1,
                       focuscolor='none')
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', cls.COLORS['primary']),
                           ('active', cls.COLORS['hover'])],
                 foreground=[('selected', cls.COLORS['surface'])])
        
        # Configure buttons
        style.configure('Modern.TButton',
                       background=cls.COLORS['primary'],
                       foreground=cls.COLORS['surface'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=[16, 8])
        
        style.map('Modern.TButton',
                 background=[('active', cls.COLORS['primary_light']),
                           ('pressed', cls.COLORS['primary_dark'])])
        
        # Secondary button style
        style.configure('Secondary.TButton',
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['primary'],
                       borderwidth=1,
                       focuscolor='none',
                       padding=[16, 8])
        
        style.map('Secondary.TButton',
                 background=[('active', cls.COLORS['hover'])],
                 bordercolor=[('!active', cls.COLORS['border']),
                            ('active', cls.COLORS['primary'])])
        
        # Configure entries
        style.configure('Modern.TEntry',
                       fieldbackground=cls.COLORS['surface'],
                       borderwidth=1,
                       insertcolor=cls.COLORS['text_primary'],
                       padding=[8, 6])
        
        style.map('Modern.TEntry',
                 bordercolor=[('focus', cls.COLORS['primary']),
                            ('!focus', cls.COLORS['border'])])
        
        # Configure frames
        style.configure('Modern.TFrame',
                       background=cls.COLORS['background'],
                       borderwidth=0)
        
        style.configure('Card.TFrame',
                       background=cls.COLORS['surface'],
                       borderwidth=1,
                       relief='solid')
        
        # Configure labels
        style.configure('Modern.TLabel',
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_primary'])
        
        style.configure('Heading.TLabel',
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['heading'])
        
        style.configure('Card.TLabel',
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'])
        
        # Configure treeview
        style.configure('Modern.Treeview',
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       fieldbackground=cls.COLORS['surface'],
                       borderwidth=1,
                       rowheight=25)
        
        style.configure('Modern.Treeview.Heading',
                       background=cls.COLORS['primary'],
                       foreground=cls.COLORS['surface'],
                       borderwidth=1,
                       relief='flat')
        
        style.map('Modern.Treeview',
                 background=[('selected', cls.COLORS['primary_light'])])

class StatusBar(ttk.Frame):
    """Modern status bar with icons and messages"""
    
    def __init__(self, parent):
        super().__init__(parent, style='Modern.TFrame')
        
        self.status_var = tk.StringVar(value="Ready")
        
        # Status label
        self.status_label = ttk.Label(self, textvariable=self.status_var,
                                    style='Modern.TLabel', font=ModernTheme.FONTS['small'])
        self.status_label.pack(side='left', padx=8, pady=4)
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        
    def set_status(self, message, show_progress=False):
        self.status_var.set(message)
        if show_progress:
            self.progress.pack(side='right', padx=8, pady=4)
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.pack_forget()
