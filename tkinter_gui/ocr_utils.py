"""
CuisineCraft OCR Utilities Module
Handles OCR processing and receipt parsing.
"""

import pytesseract
import cv2
import re
import datetime
import logging
import pandas as pd
from typing import List, Optional, Tuple

from models import ReceiptItem

logger = logging.getLogger('CuisineCraft')

def perform_ocr(file_path: str) -> str:
    """Perform OCR on the given image file"""
    logger.debug(f"Performing OCR on {file_path}")
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=custom_config)
    logger.debug(f"Extracted text from OCR: \n{text[:200]}...")
    return text

def parse_receipt(text: str) -> Tuple[List[ReceiptItem], str, str]:
    """Parse the raw OCR text to extract receipt items, shop, and date."""
    logger.debug("Parsing OCR text.")
    items = []
    lines = text.split('\n')
    
    shop_name = "Unknown Shop"
    known_shops = ['lidl', 'aldi', 'colruyt', 'delhaize', 'carrefour']
    for line in lines:
        for shop in known_shops:
            if shop in line.lower():
                shop_name = shop.capitalize()
                break
        if shop_name != "Unknown Shop":
            break

    date_str = datetime.date.today().strftime('%Y-%m-%d')
    date_regex = re.compile(r'(\d{2}[-/]\d{2}[-/]\d{4})')
    for line in lines:
        match = date_regex.search(line)
        if match:
            try:
                date_obj = datetime.datetime.strptime(match.group(1).replace('-', '/'), '%d/%m/%Y')
                date_str = date_obj.strftime('%Y-%m-%d')
                break
            except ValueError:
                pass

    item_regex = re.compile(r'^(.*?)\s+([\d,]+\.\d{2})\s*$')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = item_regex.search(line)
        if match:
            item_name = match.group(1).strip()
            price_str = match.group(2).replace(',', '')
            price = float(price_str)
            
            item_name = re.sub(r'^\d+\s*', '', item_name)

            items.append(ReceiptItem(
                item_name=item_name,
                price=price,
                shop=shop_name,
                price_date=date_str
            ))
    logger.info(f"Parsed {len(items)} items from receipt text.")
    return items, shop_name, date_str

def find_ingredient_price(ingredient_name: str, receipt_items_df: pd.DataFrame) -> Tuple[Optional[float], Optional[str]]:
    """Find the price of an ingredient from receipt data."""
    if receipt_items_df.empty:
        return None, None
        
    for _, row in receipt_items_df.iterrows():
        if ingredient_name.lower() in row['item_name'].lower():
            return row['price'], row['shop']
    return None, None