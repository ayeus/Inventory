import pandas as pd
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

EXCEL_FILE = os.path.join(os.path.dirname(__file__), '../data/inventory_data.xlsx')

def load_excel_data():
    try:
        logger.debug("Loading Excel file from: %s", EXCEL_FILE)
        if not os.path.exists(EXCEL_FILE):
            logger.error("Excel file not found at: %s", EXCEL_FILE)
            return {}
        
        # Load all sheets into a dictionary
        excel_data = pd.read_excel(EXCEL_FILE, sheet_name=None)
        inventory_data = {}
        
        for sheet_name, df in excel_data.items():
            logger.debug("Processing sheet: %s", sheet_name)
            # Clean column names
            df.columns = df.columns.str.strip().str.replace('\n', ' ').str.lower()
            
            # Map common column name variations to standard keys
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                # Serial number variations
                if 's.no' in col_lower or 'sno' in col_lower or 'sl. no' in col_lower or 'serial' in col_lower:
                    column_mapping[col] = 'serial_number'
                # Item name variations
                elif 'name' in col_lower or 'item' in col_lower or 'description' in col_lower or 'equipment' in col_lower:
                    column_mapping[col] = 'item_name'
                # Stock/quantity variations
                elif 'quantity' in col_lower or 'stock' in col_lower:
                    column_mapping[col] = 'stock_quantity'
                else:
                    # Keep other columns as-is (but lowercase)
                    column_mapping[col] = col_lower
            
            # Rename columns using the mapping
            df = df.rename(columns=column_mapping)
            # Replace NaN with None (for JSON serialization)
            df = df.replace({np.nan: None})
            # Convert to list of dictionaries
            inventory_data[sheet_name] = df.to_dict(orient='records')
            # Ensure stock_quantity is initialized if not present
            for item in inventory_data[sheet_name]:
                if 'stock_quantity' not in item or item['stock_quantity'] is None:
                    item['stock_quantity'] = 0
        
        return inventory_data
    except Exception as e:
        logger.error("Error loading Excel data: %s", str(e))
        return {}

def save_to_excel(inventory_data):
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            for sheet_name, data in inventory_data.items():
                df = pd.DataFrame(data)
                # Replace None with NaN for Excel compatibility
                df = df.fillna(np.nan)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        logger.error("Error saving to Excel: %s", str(e))
        raise