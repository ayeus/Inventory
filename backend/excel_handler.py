import openpyxl
import os
import logging

logger = logging.getLogger(__name__)

# File to read the original inventory data
EXCEL_FILE = os.path.join(os.path.dirname(__file__), '../data/inventory_data.xlsx')

# File to save new stock entries
STOCK_ENTRIES_FILE = os.path.join(os.path.dirname(__file__), '../data/stock_entries.xlsx')

def load_excel_data():
    try:
        logger.debug("Loading Excel file from: %s", EXCEL_FILE)
        if not os.path.exists(EXCEL_FILE):
            logger.error("Excel file not found at: %s", EXCEL_FILE)
            return {}
        
        # Load the workbook with openpyxl
        workbook = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
        inventory_data = {}
        
        for sheet_name in workbook.sheetnames:
            logger.debug("Processing sheet: %s", sheet_name)
            sheet = workbook[sheet_name]
            
            # Get dimensions of the sheet
            if not sheet.dimensions or sheet.dimensions == 'A1:A1':
                logger.warning("Sheet %s appears to be empty (dimensions: %s)", sheet_name, sheet.dimensions)
                # Check if there are any non-empty cells
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
            
            # Get the actual used range
            min_row = 1  # Start from the first row
            max_row = max(sheet.max_row, 1)
            min_col = 1
            max_col = max(sheet.max_column, 1)
            
            # Adjust max_row and max_col to include all non-empty cells
            for row in sheet.rows:
                for cell in row:
                    if cell.value is not None:
                        max_row = max(max_row, cell.row)
                        max_col = max(max_col, cell.column)
            
            logger.debug("Sheet %s dimensions: min_row=%d, max_row=%d, min_col=%d, max_col=%d", 
                        sheet_name, min_row, max_row, min_col, max_col)
            
            # Extract all cells as a grid, ignoring formatting
            grid = []
            for row_idx in range(min_row, max_row + 1):
                row_data = []
                for col_idx in range(min_col, max_col + 1):
                    cell = sheet.cell(row=row_idx, column=col_idx)
                    value = cell.value if cell.value is not None else ''
                    row_data.append(value)
                if any(cell != '' for cell in row_data):  # Only add non-empty rows
                    grid.append(row_data)
            
            logger.debug("Grid for sheet %s: %s", sheet_name, grid)
            inventory_data[sheet_name] = grid
        
        return inventory_data
    except Exception as e:
        logger.error("Error loading Excel data: %s", str(e))
        return {}

def save_stock_entry(category, headers, new_entry):
    try:
        logger.debug("Saving stock entry for category: %s", category)
        logger.debug("Headers: %s", headers)
        logger.debug("New entry: %s", new_entry)

        # Ensure the data directory exists
        data_dir = os.path.dirname(STOCK_ENTRIES_FILE)
        if not os.path.exists(data_dir):
            logger.debug("Creating data directory: %s", data_dir)
            os.makedirs(data_dir)

        # Load the stock entries workbook if it exists, otherwise create a new one
        if os.path.exists(STOCK_ENTRIES_FILE):
            logger.debug("Loading existing stock entries file: %s", STOCK_ENTRIES_FILE)
            workbook = openpyxl.load_workbook(STOCK_ENTRIES_FILE)
        else:
            logger.debug("Creating new stock entries file: %s", STOCK_ENTRIES_FILE)
            workbook = openpyxl.Workbook()
            # Remove the default sheet created by openpyxl
            workbook.remove(workbook.active)

        # Check if the category sheet exists, if not create it
        if category not in workbook.sheetnames:
            logger.debug("Creating new sheet for category: %s", category)
            sheet = workbook.create_sheet(title=category)
            # Add headers to the new sheet
            for col_idx, header in enumerate(headers, start=1):
                cell = sheet.cell(row=1, column=col_idx)
                cell.value = header
        else:
            sheet = workbook[category]

        # Find the next available row (after the header row)
        next_row = sheet.max_row + 1 if sheet.max_row > 1 else 2

        # Write the new entry to the sheet
        for col_idx, value in enumerate(new_entry, start=1):
            cell = sheet.cell(row=next_row, column=col_idx)
            cell.value = value

        # Save the workbook
        workbook.save(STOCK_ENTRIES_FILE)
        logger.debug("Saved stock entry to %s, sheet %s: %s", STOCK_ENTRIES_FILE, category, new_entry)
        return True, "Stock entry added successfully."
    except Exception as e:
        logger.error("Error saving stock entry: %s", str(e))
        return False, f"Error saving stock entry: {str(e)}"