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
        # Map sanitized category back to original
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == category), None)
        if original_category:
            return inventory_data.get(original_category, [])
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
            if item['S.No.'] == int(item_id):
                item['stock'] = new_stock
                return True
        return False
    except Exception as e:
        logger.error("Error in update_inventory: %s", str(e))
        return False