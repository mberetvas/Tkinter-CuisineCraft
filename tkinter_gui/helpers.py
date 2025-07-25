"""
CuisineCraft Helper Functions Module
Contains various utility and helper functions.
"""

import pandas as pd
from typing import Optional, Tuple

def find_ingredient_price(ingredient_name: str, receipt_items_df: pd.DataFrame) -> Tuple[Optional[float], Optional[str]]:
    """Find the price of an ingredient from receipt data."""
    if receipt_items_df.empty:
        return None, None
        
    for _, row in receipt_items_df.iterrows():
        if ingredient_name.lower() in row['item_name'].lower():
            return row['price'], row['shop']
    return None, None