import logging

logger = logging.getLogger(__name__)

def process_restock(inventory_data, category, item_id, quantity, headers):
    try:
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == category), None)
        if not original_category:
            return False, "Category not found"
        if not headers or not inventory_data[original_category]:
            return False, "No data available for this category"
        # Find the stock column dynamically (headers are now the first row of the grid)
        stock_column_idx = None
        item_name_column_idx = None
        serial_column_idx = None
        for col_idx, header in enumerate(inventory_data[original_category][0]):
            if 'quantity' in str(header).lower() or 'stock' in str(header).lower():
                stock_column_idx = col_idx
            if 'name' in str(header).lower() or 'item' in str(header).lower() or 'description' in str(header).lower() or 'equipment' in str(header).lower():
                item_name_column_idx = col_idx
            if 's.no' in str(header).lower() or 'sno' in str(header).lower() or 'sl. no' in str(header).lower():
                serial_column_idx = col_idx
        if stock_column_idx is None:
            return False, "No stock column found in this category"
        if serial_column_idx is None:
            return False, "No serial number column found in this category"
        if item_name_column_idx is None:
            item_name_column_idx = None  # We'll use "Unknown" if no item name column is found
        # Update the stock for the matching item
        for row in inventory_data[original_category][1:]:  # Skip the header row
            if len(row) > serial_column_idx and row[serial_column_idx] == int(item_id):
                if len(row) > stock_column_idx:
                    current_stock = row[stock_column_idx]
                    if not isinstance(current_stock, (int, float)):
                        current_stock = 0
                    row[stock_column_idx] = current_stock + quantity
                    item_name = row[item_name_column_idx] if item_name_column_idx is not None and len(row) > item_name_column_idx else 'Unknown'
                    return True, f"Restocked {quantity} of {item_name}."
        return False, "Item not found."
    except Exception as e:
        logger.error("Error in process_restock: %s", str(e))
        return False, "Error processing restock"