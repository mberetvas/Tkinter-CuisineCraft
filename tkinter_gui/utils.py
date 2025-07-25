"""
CuisineCraft Utilities
Helper functions for parsing, validation, and file operations
"""

import re
import time
import csv
import logging
from typing import List
from tkinter_gui.config import CSV_DELIMITER

logger = logging.getLogger('CuisineCraft')

def parse_cooking_time(cooking_time_str: str) -> int:
    """Parse cooking time string and convert to integer minutes"""
    if not cooking_time_str:
        return 0
    
    # Remove common words and convert to lowercase
    time_str = cooking_time_str.lower().strip()
    time_str = time_str.replace('minutes', '').replace('minute', '')
    time_str = time_str.replace('mins', '').replace('min', '')
    time_str = time_str.replace('hours', '').replace('hour', '')
    time_str = time_str.replace('hrs', '').replace('hr', '').replace('h', '')
    time_str = time_str.strip()
    
    # Try to extract numbers
    hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hour|hr|h)', cooking_time_str.lower())
    minute_match = re.search(r'(\d+)\s*(?:minute|min|m)', cooking_time_str.lower())
    
    total_minutes = 0
    
    if hour_match:
        hours = float(hour_match.group(1))
        total_minutes += int(hours * 60)
    
    if minute_match:
        minutes = int(minute_match.group(1))
        total_minutes += minutes
    
    # If no specific time format found, try to extract just the number
    if total_minutes == 0:
        number_match = re.search(r'(\d+)', time_str)
        if number_match:
            # Assume it's minutes if it's a reasonable number (< 300)
            num = int(number_match.group(1))
            if num <= 300:  # Assume minutes
                total_minutes = num
            else:  # Might be in some other format, default to 0
                total_minutes = 0
    
    return total_minutes

def export_to_text(file_path: str, meals: List[dict], grouped_ingredients: dict) -> None:
    """Export menu to text format with URLs and grouped ingredients"""
    logger.info(f"Exporting week menu to text file: {file_path}")
    content = "CuisineCraft - Week Menu\n"
    content += "=" * 30 + "\n\n"
    content += "MEALS FOR THE WEEK:\n"
    content += "-" * 20 + "\n"
    
    for i, meal_data in enumerate(meals, 1):
        meal_name = meal_data['name']
        meal_url = meal_data['url']
        content += f"{i}. {meal_name}"
        if meal_url:
            content += f" ({meal_url})"
        content += "\n"
    
    content += "\n\nSHOPPING LIST:\n"
    content += "-" * 15 + "\n"
    
    # Sort meals by name for consistent output
    sorted_meal_names = sorted(grouped_ingredients.keys())

    for meal_name in sorted_meal_names:
        ingredients_for_meal = grouped_ingredients[meal_name]
        content += f"\n--- Ingredients for {meal_name} ---\n"
        for ingredient in ingredients_for_meal:
            content += f"• {ingredient['name']}, {ingredient['amount']}, {ingredient['unit']}\n"
    
    content += f"\n\nGenerated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def export_to_csv(file_path: str, meals: List[dict], grouped_ingredients: dict) -> None:
    """Export menu to CSV format with URLs and grouped ingredients"""
    logger.info(f"Exporting week menu to CSV file: {file_path}")
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=CSV_DELIMITER)
        
        # Write header
        writer.writerow(['CuisineCraft Week Menu Export'])
        writer.writerow([f'Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])  # Empty row
        
        # Write meals
        writer.writerow(['Week Meals'])
        writer.writerow(['Day', 'Meal', 'URL'])
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, meal_data in enumerate(meals):
            day = days[i] if i < len(days) else f'Day {i+1}'
            writer.writerow([day, meal_data['name'], meal_data['url']])
        
        writer.writerow([])  # Empty row
        
        # Write ingredients grouped by meal
        writer.writerow(['Shopping List (Grouped by Meal)'])
        
        # Sort meals by name for consistent output
        sorted_meal_names = sorted(grouped_ingredients.keys())

        for meal_name in sorted_meal_names:
            writer.writerow([]) # Empty row for separation
            writer.writerow([f'Ingredients for {meal_name}'])
            writer.writerow(['Ingredient', 'Amount', 'Unit'])
            ingredients_for_meal = grouped_ingredients[meal_name]
            for ingredient in ingredients_for_meal:
                writer.writerow([ingredient['name'], ingredient['amount'], ingredient['unit']])
