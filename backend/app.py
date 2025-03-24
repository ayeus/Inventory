import os
from flask import Flask, render_template, request, jsonify
from excel_handler import load_excel_data, save_stock_entry
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

# Load inventory data
logger.debug("Loading inventory data...")
inventory_data = load_excel_data()
logger.debug("Inventory data loaded: %s", inventory_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product_table', methods=['GET', 'POST'])
def product_table():
    try:
        categories = get_categories(inventory_data)
        if not categories:
            return render_template('product_table.html', categories=[], selected_category=None, grid_data=[], error="No categories available")
        # Default to the first category's sanitized name
        selected_sanitized_category = request.form.get('category', categories[0][0])
        # Find the original category name
        selected_original_category = next((orig for sanitized, orig in categories if sanitized == selected_sanitized_category), None)
        grid_data = get_inventory(inventory_data, selected_sanitized_category)
        if not grid_data:
            logger.warning("No data found for category: %s", selected_sanitized_category)
            return render_template('product_table.html', categories=categories, selected_category=selected_sanitized_category, grid_data=[], error="No data available for this category")
        return render_template('product_table.html', categories=categories, selected_category=selected_sanitized_category, grid_data=grid_data, error=None)
    except Exception as e:
        logger.error("Error in product_table route: %s", str(e))
        return render_template('product_table.html', categories=[], selected_category=None, grid_data=[], error="Failed to load product table")

@app.route('/stock_counter', methods=['GET', 'POST'])
def stock_counter():
    try:
        categories = get_categories(inventory_data)
        if not categories:
            return render_template('stock_counter.html', categories=[], selected_category=None, grid_data=[], headers=[], error="No categories available")
        # Default to the first category's sanitized name
        selected_sanitized_category = request.form.get('category', categories[0][0])
        # Find the original category name
        selected_original_category = next((orig for sanitized, orig in categories if sanitized == selected_sanitized_category), None)
        grid_data = get_inventory(inventory_data, selected_sanitized_category)
        
        # Get the headers for the selected category (first row of the grid)
        headers = grid_data[0] if grid_data else []
        
        if request.method == 'POST' and 'add_entry' in request.form:
            logger.debug("Received form data: %s", request.form)
            # Collect the new entry from the form
            new_entry = []
            for header in headers:
                # Sanitize the header to match the form field name
                field_name = header.replace(' ', '_').replace('.', '_').lower()
                value = request.form.get(field_name, '')
                new_entry.append(value)
            
            # Save the new entry to stock_entries.xlsx using the original category name
            success, message = save_stock_entry(selected_original_category, headers, new_entry)
            return jsonify({'success': success, 'message': message})
        
        if not grid_data:
            logger.warning("No data found for category: %s", selected_sanitized_category)
            return render_template('stock_counter.html', categories=categories, selected_category=selected_sanitized_category, grid_data=[], headers=headers, error="No data available for this category")
        return render_template('stock_counter.html', categories=categories, selected_category=selected_sanitized_category, grid_data=grid_data, headers=headers, error=None)
    except Exception as e:
        logger.error("Error in stock_counter route: %s", str(e))
        return jsonify({'success': False, 'message': f"Error in stock_counter: {str(e)}"}), 500

@app.route('/sales_reform', methods=['GET', 'POST'])
def sales_reform():
    try:
        categories = get_categories(inventory_data)
        if not categories:
            return render_template('sales_reform.html', categories=[], selected_category=None, grid_data=[], error="No categories available")
        selected_sanitized_category = request.form.get('category', categories[0][0])
        grid_data = get_inventory(inventory_data, selected_sanitized_category)
        if request.method == 'POST' and 'sale' in request.form:
            item_id = request.form['item_id']
            quantity = int(request.form['quantity'])
            success, message = process_sale(inventory_data, selected_sanitized_category, item_id, quantity, grid_data[0] if grid_data else [])
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
    try:
        logger.debug("Fetching inventory for category: %s", category)
        grid_data = get_inventory(inventory_data, category)
        logger.debug("Inventory data for %s: %s", category, grid_data)
        return jsonify(grid_data)
    except Exception as e:
        logger.error("Error in api_inventory route: %s", str(e))
        return jsonify({'error': 'Failed to load inventory'}), 500

if __name__ == '__main__':
    app.run(debug=True)