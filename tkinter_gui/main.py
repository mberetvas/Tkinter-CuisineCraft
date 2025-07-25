"""
CuisineCraft Main Entry Point
Run the application from here
"""

import tkinter as tk
from tkinter_gui.logger import logger
from tkinter_gui.gui import CuisineCraftModernGUI
from tkinter import messagebox

def main():
    try:
        root = tk.Tk()
        # Instantiate the main GUI. The constructor sets up all widgets and event bindings.
        # We do not need to keep a reference to the object, as all logic is managed internally.
        CuisineCraftModernGUI(root)
        root.mainloop()
    except Exception as e:
        logger.exception("Failed to start CuisineCraft")
        messagebox.showerror(
            "Startup Error",
            f"Failed to start CuisineCraft: {str(e)}"
        )

if __name__ == "__main__":
    main()
