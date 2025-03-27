import mysql.connector
from mysql.connector import Error
import logging

logger = logging.getLogger(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'Aasu@1234',  # Replace with your MySQL password
    'database': 'InventoryDB'
}

def get_db_connection():
    try:
        logger.debug("Attempting to connect to MySQL database with config: host=%s, user=%s, database=%s", 
                     db_config['host'], db_config['user'], db_config['database'])
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            logger.debug("Successfully connected to MySQL database")
            return connection
        else:
            logger.error("Connection established but not connected")
            return None
    except Error as e:
        logger.error("Error connecting to MySQL database: %s", str(e))
        return None
    except Exception as e:
        logger.error("Unexpected error while connecting to MySQL database: %s", str(e))
        return None

def close_db_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        logger.debug("MySQL connection closed")

def get_tables():
    connection = get_db_connection()
    if not connection:
        logger.warning("Failed to get database connection, returning empty table list")
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        logger.debug("Tables in database: %s", tables)
        return tables
    except Error as e:
        logger.error("Error fetching tables: %s", str(e))
        return []
    finally:
        close_db_connection(connection)

def get_table_data(table_name):
    connection = get_db_connection()
    if not connection:
        logger.warning("Failed to get database connection, returning empty data")
        return []
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cursor.description]
        data = [list(row) for row in cursor.fetchall()]
        data.insert(0, columns)  # Insert column headers as the first row
        logger.debug("Data fetched from table %s: %s", table_name, data)
        return data
    except Error as e:
        logger.error("Error fetching data from table %s: %s", table_name, str(e))
        return []
    finally:
        close_db_connection(connection)

def add_table_entry(table_name, data):
    connection = get_db_connection()
    if not connection:
        return False, "Failed to connect to database"
    try:
        cursor = connection.cursor()
        # Get column names (excluding 'id' since it's AUTO_INCREMENT)
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [col[0] for col in cursor.fetchall() if col[0] != 'id']
        if len(columns) != len(data):
            return False, "Data length does not match number of columns"
        
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        cursor.execute(query, data)
        connection.commit()
        logger.debug("Added entry to table %s: %s", table_name, data)
        return True, "Entry added successfully"
    except Error as e:
        logger.error("Error adding entry to table %s: %s", table_name, str(e))
        return False, f"Error adding entry: {str(e)}"
    finally:
        close_db_connection(connection)

def update_table_entry(table_name, row_id, data):
    connection = get_db_connection()
    if not connection:
        return False, "Failed to connect to database"
    try:
        cursor = connection.cursor()
        # Get column names (excluding 'id')
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [col[0] for col in cursor.fetchall() if col[0] != 'id']
        if len(columns) != len(data):
            return False, "Data length does not match number of columns"
        
        set_clause = ', '.join([f"{col} = %s" for col in columns])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        cursor.execute(query, data + [row_id])
        connection.commit()
        logger.debug("Updated entry in table %s, id %s: %s", table_name, row_id, data)
        return True, "Entry updated successfully"
    except Error as e:
        logger.error("Error updating entry in table %s: %s", table_name, str(e))
        return False, f"Error updating entry: {str(e)}"
    finally:
        close_db_connection(connection)

def delete_table_entry(table_name, row_id):
    connection = get_db_connection()
    if not connection:
        return False, "Failed to connect to database"
    try:
        cursor = connection.cursor()
        query = f"DELETE FROM {table_name} WHERE id = %s"
        cursor.execute(query, (row_id,))
        connection.commit()
        logger.debug("Deleted entry from table %s, id %s", table_name, row_id)
        return True, "Entry deleted successfully"
    except Error as e:
        logger.error("Error deleting entry from table %s: %s", table_name, str(e))
        return False, f"Error deleting entry: {str(e)}"
    finally:
        close_db_connection(connection)

def delete_all_entries(table_name):
    connection = get_db_connection()
    if not connection:
        return False, "Failed to connect to database"
    try:
        cursor = connection.cursor()
        query = f"DELETE FROM {table_name}"
        cursor.execute(query)
        connection.commit()
        logger.debug("Deleted all entries from table %s", table_name)
        return True, f"All entries in table '{table_name}' deleted successfully"
    except Error as e:
        logger.error("Error deleting all entries from table %s: %s", table_name, str(e))
        return False, f"Error deleting all entries: {str(e)}"
    finally:
        close_db_connection(connection)