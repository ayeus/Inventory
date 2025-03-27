import logging

logger = logging.getLogger(__name__)

def get_categories(inventory_data):
    try:
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
    logger.warning("update_inventory is deprecated; inventory is updated directly in Excel file")
    return True