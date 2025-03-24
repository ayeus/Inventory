import logging

logger = logging.getLogger(__name__)

def get_categories(inventory_data):
    try:
        # Return a list of tuples: (sanitized_category, original_category)
        categories = [(cat.replace(',', '_').replace(' ', '_'), cat) for cat in inventory_data.keys()]
        logger.debug("Categories (sanitized, original): %s", categories)
        return categories
    except Exception as e:
        logger.error("Error in get_categories: %s", str(e))
        return []

def get_inventory(inventory_data, sanitized_category):
    try:
        logger.debug("Original inventory keys: %s", list(inventory_data.keys()))
        logger.debug("Looking for sanitized category: %s", sanitized_category)
        # Map sanitized category back to original
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == sanitized_category), None)
        logger.debug("Mapped to original category: %s", original_category)
        if original_category:
            data = inventory_data.get(original_category, [])
            logger.debug("Data for %s: %s", original_category, data)
            return data
        logger.warning("Category %s not found in inventory data", sanitized_category)
        return []
    except Exception as e:
        logger.error("Error in get_inventory: %s", str(e))
        return []

def update_inventory(inventory_data, sanitized_category, item_id, new_stock, headers):
    try:
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == sanitized_category), None)
        if not original_category:
            return False
        if not headers or not inventory_data[original_category]:
            return False
        # Find the stock column dynamically (headers are now the first row of the grid)
        stock_column_idx = None
        for col_idx, header in enumerate(inventory_data[original_category][0]):
            if 'quantity' in str(header).lower() or 'stock' in str(header).lower():
                stock_column_idx = col_idx
                break
        if stock_column_idx is None:
            return False  # No stock column found
        # Find the serial number column
        serial_column_idx = None
        for col_idx, header in enumerate(inventory_data[original_category][0]):
            if 's.no' in str(header).lower() or 'sno' in str(header).lower() or 'sl. no' in str(header).lower():
                serial_column_idx = col_idx
                break
        if serial_column_idx is None:
            return False  # No serial number column found
        # Update the stock for the matching item
        for row in inventory_data[original_category][1:]:  # Skip the header row
            if len(row) > serial_column_idx and row[serial_column_idx] == int(item_id):
                if len(row) > stock_column_idx:
                    row[stock_column_idx] = new_stock
                    return True
        return False
    except Exception as e:
        logger.error("Error in update_inventory: %s", str(e))
        return False