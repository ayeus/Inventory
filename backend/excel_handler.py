import pandas as pd
import os
import logging

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
            df.columns = df.columns.str.strip().str.replace('\n', ' ')
            df = df.rename(columns={
                'S.No.': 'S.No.',
                'S.NO.': 'S.No.',
                'Sl. No.': 'S.No.',
                'NAME OF ITEMS': 'Name of Items',
                'Equipment’s': 'Equipment’s',
                'Item description': 'Item_description',
                'QUANTITY': 'QUANTITY (IN 2023-2024)',
                'stock': 'stock'
            })
            # Convert to list of dictionaries
            inventory_data[sheet_name] = df.to_dict(orient='records')
            # Initialize stock if not present
            for item in inventory_data[sheet_name]:
                if 'stock' not in item:
                    item['stock'] = item.get('QUANTITY (IN 2023-2024)', 0)
        
        return inventory_data
    except Exception as e:
        logger.error("Error loading Excel data: %s", str(e))
        return {}

def save_to_excel(inventory_data):
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            for sheet_name, data in inventory_data.items():
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        logger.error("Error saving to Excel: %s", str(e))
        raise