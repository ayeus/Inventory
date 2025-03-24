import logging

logger = logging.getLogger(__name__)

def process_sale(inventory_data, category, item_id, quantity):
    try:
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == category), None)
        if not original_category:
            return False, "Category not found"
        for item in inventory_data[original_category]:
            if item['serial_number'] == int(item_id):
                current_stock = item.get('stock_quantity', 0)
                if current_stock >= quantity:
                    item['stock_quantity'] = current_stock - quantity
                    item_name = item.get('item_name', 'Unknown')
                    return True, f"Sold {quantity} of {item_name}."
                else:
                    return False, f"Not enough stock (Available: {current_stock})."
        return False, "Item not found."
    except Exception as e:
        logger.error("Error in process_sale: %s", str(e))
        return False, "Error processing sale"