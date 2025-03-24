import logging

logger = logging.getLogger(__name__)

def get_categories(inventory_data):
    try:
        # Sanitize category names to avoid issues in URLs
        categories = [cat.replace(',', '_').replace(' ', '_') for cat in inventory_data.keys()]
        logger.debug("Sanitized categories: %s", categories)
        return categories
    except Exception as e:
        logger.error("Error in get_categories: %s", str(e))
        return []

def get_inventory(inventory_data, category):
    try:
        logger.debug("Original inventory keys: %s", list(inventory_data.keys()))
        logger.debug("Looking for sanitized category: %s", category)
        # Map sanitized category back to original
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == category), None)
        logger.debug("Mapped to original category: %s", original_category)
        if original_category:
            data = inventory_data.get(original_category, [])
            logger.debug("Data for %s: %s", original_category, data)
            return data
        logger.warning("Category %s not found in inventory data", category)
        return []
    except Exception as e:
        logger.error("Error in get_inventory: %s", str(e))
        return []

def update_inventory(inventory_data, category, item_id, new_stock):
    try:
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == category), None)
        if not original_category:
            return False
        for item in inventory_data[original_category]:
            if item['serial_number'] == int(item_id):
                item['stock_quantity'] = new_stock
                return True
        return False
    except Exception as e:
        logger.error("Error in update_inventory: %s", str(e))
        return False