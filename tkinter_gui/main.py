"""
CuisineCraft Main Entry Point
Run the application from here
"""

import tkinter as tk
import logging
from gui import CuisineCraftModernGUI
from tkinter import messagebox

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    try:
        root = tk.Tk()
        # Instantiate the main GUI. The constructor sets up all widgets and event bindings.
        # We do not need to keep a reference to the object, as all logic is managed internally.
        CuisineCraftModernGUI(root)
        root.mainloop()
    except Exception as e:
        logging.exception("Failed to start CuisineCraft")
        messagebox.showerror(
            "Startup Error",
            f"Failed to start CuisineCraft: {str(e)}"
        )

if __name__ == "__main__":
    main()
