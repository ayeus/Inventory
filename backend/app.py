import os
from flask import Flask, render_template, request, jsonify
from excel_handler import load_excel_data, update_inventory_data, delete_category_data
from inventory import get_categories, get_inventory, update_inventory
from sales import process_sale
from restock import process_restock
import logging

# Set up the Flask app with correct template and static folder paths
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '../static'))

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load inventory data (global variable to be updated after changes)
inventory_data = load_excel_data()
logger.debug("Inventory data loaded: %s", inventory_data)

@app.route('/')
def index():
    logger.debug("Accessing index route")
    return render_template('index.html')

@app.route('/product_table', methods=['GET', 'POST'])
def product_table():
    logger.debug("Accessing product_table route, method: %s", request.method)
    try:
        categories = get_categories(inventory_data)
        if not categories:
            logger.warning("No categories available")
            return render_template('product_table.html', categories=[], selected_category=None, grid_data=[], error="No categories available")
        selected_sanitized_category = request.form.get('category', categories[0][0])
        selected_original_category = next((orig for sanitized, orig in categories if sanitized == selected_sanitized_category), None)
        grid_data = get_inventory(inventory_data, selected_sanitized_category)
        if not grid_data:
            logger.warning("No data found for category: %s", selected_sanitized_category)
            return render_template('product_table.html', categories=categories, selected_category=selected_sanitized_category, grid_data=[], error="No data available for this category")
        logger.debug("Rendering product_table with categories: %s, selected: %s", categories, selected_sanitized_category)
        return render_template('product_table.html', categories=categories, selected_category=selected_sanitized_category, grid_data=grid_data, error=None)
    except Exception as e:
        logger.error("Error in product_table route: %s", str(e))
        return render_template('product_table.html', categories=[], selected_category=None, grid_data=[], error="Failed to load product table")

@app.route('/stock_counter', methods=['GET', 'POST'])
def stock_counter():
    global inventory_data
    logger.debug("Accessing stock_counter route, method: %s", request.method)
    
    # Handle POST requests (form submission, edit, delete)
    if request.method == 'POST':
        try:
            action = request.form.get('action', 'add_entry')
            logger.debug("Action received: %s", action)
            
            categories = get_categories(inventory_data)
            if not categories:
                logger.warning("No categories available in stock_counter")
                return jsonify({'success': False, 'message': "No categories available"}), 400
            
            selected_sanitized_category = request.form.get('category')
            if not selected_sanitized_category:
                logger.error("No category provided in form data")
                return jsonify({'success': False, 'message': "Category is required"}), 400
            
            selected_original_category = next((orig for sanitized, orig in categories if sanitized == selected_sanitized_category), None)
            if not selected_original_category:
                logger.error("Invalid category: %s", selected_sanitized_category)
                return jsonify({'success': False, 'message': "Invalid category"}), 400
            
            grid_data = get_inventory(inventory_data, selected_sanitized_category)
            if not grid_data:
                logger.warning("No data found for category: %s", selected_sanitized_category)
                return jsonify({'success': False, 'message': "No data available for this category"}), 400
            
            headers = grid_data[0] if grid_data else []
            valid_headers = [header for header in headers if header and str(header).strip() != '']
            logger.debug("Valid headers for category %s: %s", selected_sanitized_category, valid_headers)
            
            if not valid_headers:
                logger.error("No valid headers found for category: %s", selected_sanitized_category)
                return jsonify({'success': False, 'message': "No valid columns found in the category"}), 400
            
            if action == 'add_entry':
                logger.debug("Received POST request for stock_counter (add_entry)")
                logger.debug("Form data: %s", dict(request.form))
                
                new_entry = []
                for header in valid_headers:
                    field_name = header.replace(' ', '_').replace('.', '_').lower()
                    value = request.form.get(field_name, '')
                    new_entry.append(value)
                logger.debug("New entry to be added: %s", new_entry)
                
                success, message = update_inventory_data(selected_original_category, valid_headers, new_entry)
                logger.debug("Update result: success=%s, message=%s", success, message)
                if success:
                    inventory_data.clear()
                    inventory_data.update(load_excel_data())
                    message = "Item successfully added/updated in inventory."
                else:
                    message = f"Failed to add/update item: {message}"
                return jsonify({'success': success, 'message': message})
            
            elif action == 'edit_entry':
                logger.debug("Received POST request for stock_counter (edit_entry)")
                logger.debug("Form data: %s", dict(request.form))
                
                row_index = int(request.form.get('row_index')) + 1  # Adjust for header row
                edited_entry = []
                for header in valid_headers:
                    field_name = header.replace(' ', '_').replace('.', '_').lower()
                    value = request.form.get(field_name, '')
                    edited_entry.append(value)
                logger.debug("Edited entry at row %d: %s", row_index, edited_entry)
                
                success, message = update_inventory_data(selected_original_category, valid_headers, edited_entry, row_index=row_index)
                if success:
                    inventory_data.clear()
                    inventory_data.update(load_excel_data())
                    message = "Item successfully updated in inventory."
                else:
                    message = f"Failed to update item: {message}"
                return jsonify({'success': success, 'message': message})
            
            elif action == 'delete_category':
                logger.debug("Received POST request for stock_counter (delete_category)")
                success, message = delete_category_data(selected_original_category)
                if success:
                    inventory_data.clear()
                    inventory_data.update(load_excel_data())
                    message = f"All items in category '{selected_original_category}' deleted successfully."
                else:
                    message = f"Failed to delete category: {message}"
                return jsonify({'success': success, 'message': message})
            
            else:
                logger.error("Invalid action: %s", action)
                return jsonify({'success': False, 'message': "Invalid action"}), 400
        
        except Exception as e:
            logger.error("Error in stock_counter POST route: %s", str(e))
            return jsonify({'success': False, 'message': f"Failed to process request: {str(e)}"}), 500
    
    # Handle GET requests (render the page)
    try:
        categories = get_categories(inventory_data)
        if not categories:
            logger.warning("No categories available in stock_counter")
            return render_template('stock_counter.html', categories=[], selected_category=None, grid_data=[], headers=[], error="No categories available")
        
        selected_sanitized_category = request.form.get('category', categories[0][0])
        selected_original_category = next((orig for sanitized, orig in categories if sanitized == selected_sanitized_category), None)
        grid_data = get_inventory(inventory_data, selected_sanitized_category)
        
        headers = grid_data[0] if grid_data else []
        valid_headers = [header for header in headers if header and str(header).strip() != '']
        
        if not grid_data:
            logger.warning("No data found for category: %s", selected_sanitized_category)
            return render_template('stock_counter.html', categories=categories, selected_category=selected_sanitized_category, grid_data=[], headers=valid_headers, error="No data available for this category")
        
        return render_template('stock_counter.html', categories=categories, selected_category=selected_sanitized_category, grid_data=grid_data, headers=valid_headers, error=None)
    except Exception as e:
        logger.error("Error in stock_counter GET route: %s", str(e))
        return render_template('stock_counter.html', categories=[], selected_category=None, grid_data=[], headers=[], error="Failed to load stock counter page")

@app.route('/sales_reform', methods=['GET', 'POST'])
def sales_reform():
    global inventory_data
    logger.debug("Accessing sales_reform route, method: %s", request.method)
    try:
        categories = get_categories(inventory_data)
        if not categories:
            logger.warning("No categories available in sales_reform")
            return render_template('sales_reform.html', categories=[], selected_category=None, grid_data=[], error="No categories available")
        selected_sanitized_category = request.form.get('category', categories[0][0])
        grid_data = get_inventory(inventory_data, selected_sanitized_category)
        if request.method == 'POST' and 'sale' in request.form:
            logger.debug("Received POST request for sales_reform")
            item_id = request.form['item_id']
            quantity = int(request.form['quantity'])
            success, message = process_sale(inventory_data, selected_sanitized_category, item_id, quantity, grid_data[0] if grid_data else [])
            if success:
                inventory_data.clear()
                inventory_data.update(load_excel_data())
                grid_data = get_inventory(inventory_data, selected_sanitized_category)
            return jsonify({'success': success, 'message': message})
        if not grid_data:
            logger.warning("No data found for category: %s", selected_sanitized_category)
            return render_template('sales_reform.html', categories=categories, selected_category=selected_sanitized_category, grid_data=[], error="No data available for this category")
        return render_template('sales_reform.html', categories=categories, selected_category=selected_sanitized_category, grid_data=grid_data, error=None)
    except Exception as e:
        logger.error("Error in sales_reform route: %s", str(e))
        return render_template('sales_reform.html', categories=[], selected_category=None, grid_data=[], error="Failed to load sales reform")

@app.route('/api/inventory/<category>', methods=['GET'])
def api_inventory(category):
    logger.debug("Accessing api_inventory route for category: %s", category)
    try:
        grid_data = get_inventory(inventory_data, category)
        logger.debug("Inventory data for %s: %s", category, grid_data)
        return jsonify(grid_data)
    except Exception as e:
        logger.error("Error in api_inventory route: %s", str(e))
        return jsonify({'error': 'Failed to load inventory'}), 500

if __name__ == '__main__':
    app.run(debug=True)