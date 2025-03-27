import logging
from excel_handler import load_excel_data

logger = logging.getLogger(__name__)

def process_sale(inventory_data, sanitized_category, item_id, quantity, headers):
    try:
        logger.debug("Processing sale for category %s, item %s, quantity %d", sanitized_category, item_id, quantity)
        original_category = next((cat for cat in inventory_data.keys() if cat.replace(',', '_').replace(' ', '_') == sanitized_category), None)
        if not original_category:
            logger.error("Category %s not found", sanitized_category)
            return False, "Category not found"

        s_no_idx = None
        stock_idx = None
        for col_idx, header in enumerate(headers):
            header_lower = str(header).lower()
            if 's.no' in header_lower or 'sno' in header_lower or 'sl. no' in header_lower:
                s_no_idx = col_idx
            if 'quantity' in header_lower or 'list' in header_lower or 'stock' in header_lower:
                stock_idx = col_idx

        if s_no_idx is None or stock_idx is None:
            logger.error("Required columns (S.No., Stock) not found in headers: %s", headers)
            return False, "Required columns not found"

        grid_data = inventory_data.get(original_category, [])
        if len(grid_data) <= 1:
            return False, "No items in this category"

        item_found = False
        for row in grid_data[1:]:
            if str(row[s_no_idx]) == str(item_id):
                current_stock = int(row[stock_idx]) if row[stock_idx] and str(row[stock_idx]).isdigit() else 0
                if current_stock < quantity:
                    return False, "Insufficient stock"
                new_stock = current_stock - quantity
                row[stock_idx] = new_stock
                item_found = True
                break

        if not item_found:
            return False, "Item not found"

        # Since we're not editing the Excel file, just return success
        return True, "Sale recorded successfully (Excel file not modified)"
    except Exception as e:
        logger.error("Error in process_sale: %s", str(e))
        return False, f"Error processing sale: {str(e)}"