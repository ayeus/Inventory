import os
from flask import Flask, render_template, request, jsonify
from excel_handler import load_excel_data
from inventory import get_categories, get_inventory, update_inventory
from sales import process_sale
from restock import process_restock
from db import get_tables, get_table_data, add_table_entry, update_table_entry, delete_table_entry, delete_all_entries
import logging

# Set up the Flask app with correct template and static folder paths
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '../static'))

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load inventory data from Excel (for Product Table and Sales Reform)
inventory_data = load_excel_data()
logger.debug("Inventory data loaded from Excel: %s", inventory_data)

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
    logger.debug("Accessing stock_counter route, method: %s", request.method)
    
    # Handle POST requests (form submission, edit, delete)
    if request.method == 'POST':
        try:
            action = request.form.get('action', 'add_entry')
            logger.debug("Action received: %s", action)
            
            tables = get_tables()
            if not tables:
                logger.warning("No tables available in stock_counter")
                return jsonify({'success': False, 'message': "No tables available in the database"}), 400
            
            selected_table = request.form.get('table')
            if not selected_table:
                logger.error("No table provided in form data")
                return jsonify({'success': False, 'message': "Table is required"}), 400
            
            if selected_table not in tables:
                logger.error("Invalid table: %s", selected_table)
                return jsonify({'success': False, 'message': "Invalid table"}), 400
            
            grid_data = get_table_data(selected_table)
            if not grid_data:
                logger.warning("No data found for table: %s", selected_table)
                return jsonify({'success': False, 'message': "No data available for this table"}), 400
            
            headers = grid_data[0] if grid_data else []
            valid_headers = [header for header in headers if header != 'id']  # Exclude 'id' from form fields
            logger.debug("Valid headers for table %s: %s", selected_table, valid_headers)
            
            if not valid_headers:
                logger.error("No valid headers found for table: %s", selected_table)
                return jsonify({'success': False, 'message': "No valid columns found in the table"}), 400
            
            if action == 'add_entry':
                logger.debug("Received POST request for stock_counter (add_entry)")
                logger.debug("Form data: %s", dict(request.form))
                
                new_entry = []
                for header in valid_headers:
                    field_name = header.replace(' ', '_').replace('.', '_').lower()
                    value = request.form.get(field_name, '')
                    new_entry.append(value)
                logger.debug("New entry to be added: %s", new_entry)
                
                success, message = add_table_entry(selected_table, new_entry)
                logger.debug("Add result: success=%s, message=%s", success, message)
                if success:
                    message = "Item successfully added to the database."
                else:
                    message = f"Failed to add item: {message}"
                return jsonify({'success': success, 'message': message})
            
            elif action == 'edit_entry':
                logger.debug("Received POST request for stock_counter (edit_entry)")
                logger.debug("Form data: %s", dict(request.form))
                
                row_id = request.form.get('row_id')
                if not row_id:
                    return jsonify({'success': False, 'message': "Row ID is required for editing"}), 400
                
                edited_entry = []
                for header in valid_headers:
                    field_name = header.replace(' ', '_').replace('.', '_').lower()
                    value = request.form.get(field_name, '')
                    edited_entry.append(value)
                logger.debug("Edited entry for id %s: %s", row_id, edited_entry)
                
                success, message = update_table_entry(selected_table, row_id, edited_entry)
                if success:
                    message = "Item successfully updated in the database."
                else:
                    message = f"Failed to update item: {message}"
                return jsonify({'success': success, 'message': message})
            
            elif action == 'delete_entry':
                logger.debug("Received POST request for stock_counter (delete_entry)")
                row_id = request.form.get('row_id')
                if not row_id:
                    return jsonify({'success': False, 'message': "Row ID is required for deletion"}), 400
                
                success, message = delete_table_entry(selected_table, row_id)
                if success:
                    message = "Item successfully deleted from the database."
                else:
                    message = f"Failed to delete item: {message}"
                return jsonify({'success': success, 'message': message})
            
            elif action == 'delete_all':
                logger.debug("Received POST request for stock_counter (delete_all)")
                success, message = delete_all_entries(selected_table)
                if success:
                    message = f"All items in table '{selected_table}' deleted successfully."
                else:
                    message = f"Failed to delete all items: {message}"
                return jsonify({'success': success, 'message': message})
            
            else:
                logger.error("Invalid action: %s", action)
                return jsonify({'success': False, 'message': "Invalid action"}), 400
        
        except Exception as e:
            logger.error("Error in stock_counter POST route: %s", str(e))
            return jsonify({'success': False, 'message': f"Failed to process request: {str(e)}"}), 500
    
    # Handle GET requests (render the page)
    try:
        tables = get_tables()
        if not tables:
            logger.warning("No tables available in stock_counter")
            return render_template('stock_counter.html', tables=tables, selected_table=None, grid_data=[], headers=[], error="No tables available in the database. Please check if the database is set up correctly.")
        
        selected_table = request.args.get('table', tables[0])  # Use query parameter instead of form data
        if selected_table not in tables:
            selected_table = tables[0]
        
        grid_data = get_table_data(selected_table)
        headers = grid_data[0] if grid_data else []
        valid_headers = [header for header in headers if header != 'id']
        
        if not grid_data:
            logger.warning("No data found for table: %s", selected_table)
            return render_template('stock_counter.html', tables=tables, selected_table=selected_table, grid_data=[], headers=valid_headers, error="No data available for this table")
        
        return render_template('stock_counter.html', tables=tables, selected_table=selected_table, grid_data=grid_data, headers=valid_headers, error=None)
    except Exception as e:
        logger.error("Error in stock_counter GET route: %s", str(e))
        return render_template('stock_counter.html', tables=[], selected_table=None, grid_data=[], headers=[], error=f"Failed to load stock counter page: {str(e)}")

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

@app.route('/api/inventory/<table>', methods=['GET'])
def api_inventory(table):
    logger.debug("Accessing api_inventory route for table: %s", table)
    try:
        # Check if the request is for a MySQL table (Stock Counter) or Excel category (Product Table/Sales Reform)
        tables = get_tables()
        if table in tables:
            grid_data = get_table_data(table)
        else:
            grid_data = get_inventory(inventory_data, table)
        logger.debug("Data for %s: %s", table, grid_data)
        return jsonify(grid_data)
    except Exception as e:
        logger.error("Error in api_inventory route: %s", str(e))
        return jsonify({'error': 'Failed to load data'}), 500

if __name__ == '__main__':
    app.run(debug=True)