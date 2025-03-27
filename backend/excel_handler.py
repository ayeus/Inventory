import openpyxl
import os
import logging

logger = logging.getLogger(__name__)

# File to read the inventory data
EXCEL_FILE = os.path.join(os.path.dirname(__file__), '../data/inventory_data.xlsx')

def load_excel_data():
    try:
        logger.debug("Loading Excel file from: %s", EXCEL_FILE)
        if not os.path.exists(EXCEL_FILE):
            logger.error("Excel file not found at: %s", EXCEL_FILE)
            return {}
        
        workbook = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
        inventory_data = {}
        
        for sheet_name in workbook.sheetnames:
            logger.debug("Processing sheet: %s", sheet_name)
            sheet = workbook[sheet_name]
            
            if not sheet.dimensions or sheet.dimensions == 'A1:A1':
                logger.warning("Sheet %s appears to be empty (dimensions: %s)", sheet_name, sheet.dimensions)
                has_data = False
                for row in sheet.rows:
                    for cell in row:
                        if cell.value is not None:
                            has_data = True
                            break
                    if has_data:
                        break
                if not has_data:
                    inventory_data[sheet_name] = []
                    continue
            
            min_row = 1
            max_row = max(sheet.max_row, 1)
            min_col = 1
            max_col = max(sheet.max_column, 1)
            
            for row in sheet.rows:
                for cell in row:
                    if cell.value is not None:
                        max_row = max(max_row, cell.row)
                        max_col = max(max_col, cell.column)
            
            logger.debug("Sheet %s dimensions: min_row=%d, max_row=%d, min_col=%d, max_col=%d", 
                        sheet_name, min_row, max_row, min_col, max_col)
            
            grid = []
            for row_idx in range(min_row, max_row + 1):
                row_data = []
                for col_idx in range(min_col, max_col + 1):
                    cell = sheet.cell(row=row_idx, column=col_idx)
                    value = cell.value if cell.value is not None else ''
                    row_data.append(value)
                if any(cell != '' for cell in row_data):
                    grid.append(row_data)
            
            logger.debug("Grid for sheet %s: %s", sheet_name, grid)
            inventory_data[sheet_name] = grid
        
        return inventory_data
    except Exception as e:
        logger.error("Error loading Excel data: %s", str(e))
        return {}