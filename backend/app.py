from flask import Flask, render_template, request, jsonify
from backend.inventory import get_inventory, get_categories
from backend.sales import process_sale
from backend.restock import process_restock
from backend.excel_handler import load_excel_data, save_to_excel
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Explicitly set the template folder
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '../templates'))


# Load all sheets from Excel into a dictionary
try:
    inventory_data = load_excel_data()
    logger.debug("Successfully loaded inventory data: %s", list(inventory_data.keys()))
except Exception as e:
    logger.error("Failed to load inventory data: %s", str(e))
    inventory_data = {}

@app.route('/')
def index():
    try:
        categories = get_categories(inventory_data)
        logger.debug("Categories loaded: %s", categories)
        return render_template('index.html', categories=categories, error=None)
    except Exception as e:
        logger.error("Error in index route: %s", str(e))
        return render_template('index.html', categories=[], error="Failed to load categories. Please check the Excel file.")

@app.route('/product_table', methods=['GET', 'POST'])
def product_table():
    try:
        categories = get_categories(inventory_data)
        if not categories:
            return render_template('product_table.html', categories=[], selected_category=None, error="No categories available")
        selected_category = request.form.get('category', categories[0])
        return render_template('product_table.html', categories=categories, selected_category=selected_category, error=None)
    except Exception as e:
        logger.error("Error in product_table route: %s", str(e))
        return render_template('product_table.html', categories=[], selected_category=None, error="Failed to load product table")

@app.route('/stock_counter', methods=['GET', 'POST'])
def stock_counter():
    try:
        categories = get_categories(inventory_data)
        if not categories:
            return render_template('stock_counter.html', categories=[], selected_category=None, error="No categories available")
        selected_category = request.form.get('category', categories[0])
        if request.method == 'POST' and 'restock' in request.form:
            item_id = request.form['item_id']
            quantity = int(request.form['quantity'])
            success, message = process_restock(inventory_data, selected_category, item_id, quantity)
            save_to_excel(inventory_data)
            return jsonify({'success': success, 'message': message})
        return render_template('stock_counter.html', categories=categories, selected_category=selected_category, error=None)
    except Exception as e:
        logger.error("Error in stock_counter route: %s", str(e))
        return render_template('stock_counter.html', categories=[], selected_category=None, error="Failed to load stock counter")

@app.route('/sales_reform', methods=['GET', 'POST'])
def sales_reform():
    try:
        categories = get_categories(inventory_data)
        if not categories:
            return render_template('sales_reform.html', categories=[], selected_category=None, error="No categories available")
        selected_category = request.form.get('category', categories[0])
        if request.method == 'POST' and 'sale' in request.form:
            item_id = request.form['item_id']
            quantity = int(request.form['quantity'])
            success, message = process_sale(inventory_data, selected_category, item_id, quantity)
            save_to_excel(inventory_data)
            return jsonify({'success': success, 'message': message})
        return render_template('sales_reform.html', categories=categories, selected_category=selected_category, error=None)
    except Exception as e:
        logger.error("Error in sales_reform route: %s", str(e))
        return render_template('sales_reform.html', categories=[], selected_category=None, error="Failed to load sales reform")

@app.route('/api/inventory/<category>', methods=['GET'])
def api_inventory(category):
    try:
        data = get_inventory(inventory_data, category)
        return jsonify(data)
    except Exception as e:
        logger.error("Error in api_inventory route: %s", str(e))
        return jsonify({'error': 'Failed to load inventory'}), 500

if __name__ == '__main__':
    app.run(debug=True)