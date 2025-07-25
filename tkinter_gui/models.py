"""
CuisineCraft Models
Data classes for Recipe and Ingredient objects
"""

from dataclasses import dataclass
import datetime

@dataclass
class Recipe:
    """Recipe data model"""
    name: str
    persons: int
    cooking_time: int  # in minutes
    cuisine_origin: str
    file_location: str
    url: str
    health_grade: int

@dataclass
class Ingredient:
    """Ingredient data model"""
    amount: float
    unit: str
    name: str
    price: float = 0.0
    shop: str = ""
    price_date: str = ""

@dataclass
class ReceiptItem:
    """Receipt item data model"""
    item_name: str
    price: float
    shop: str
    price_date: str
    quantity: float = 1.0
    unit: str = ""
    receipt_image_path: str = ""

@dataclass
class WeekMenuEntry:
    """Week Menu Entry data model"""
    day: str
    recipe_id: int
    created_at: int = int(datetime.datetime.now().timestamp())
