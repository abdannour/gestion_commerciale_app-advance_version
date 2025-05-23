# Updated content for sidou2/database/database.py
import sqlite3
import os
import logging  # For logging database operations and errors
import datetime  # For default dates

# --- Database Configuration ---
# Define the name of the database file. This makes it easy to change if needed.
DATABASE_NAME = "gestion_commerciale.db"
# Construct the absolute path to the database file.
# It's placed in the parent directory of this 'database' module.
# This ensures the database is found regardless of where the main script is run from.
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", DATABASE_NAME
)

# --- Logger Configuration ---
# Get a logger instance. It's assumed to be configured in 'utils.error_handler'.
# Using a specific name for this module's logger helps in organizing log messages.
logger = logging.getLogger("inventory_app.database")  # More specific logger name


# --- Custom Exceptions (Imported from error_handler) ---
# Import custom error classes and a decorator for consistent error handling.
from utils.error_handler import handle_db_error, DatabaseError, ValidationError
from utils.validators import (
    validate_product_data,
    validate_customer_data,
    validate_required,
    validate_numeric,
)


# --- Database Connection ---
def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    This function centralizes connection creation.
    """
    try:
        # Connect to the SQLite database file.
        conn = sqlite3.connect(DATABASE_PATH)
        # Set row_factory to sqlite3.Row to access columns by their names (like dictionaries).
        conn.row_factory = sqlite3.Row
        # Enforce foreign key constraints. By default, SQLite doesn't, so this is important for data integrity.
        conn.execute("PRAGMA foreign_keys = ON;")
        logger.debug("Database connection established.")
        return conn
    except sqlite3.Error as e:
        # Log any error during connection and raise a custom DatabaseError.
        logger.error(f"Error connecting to database at {DATABASE_PATH}: {e}")
        raise DatabaseError(f"Could not connect to the database: {e}")


# --- Database Initialization ---
def initialize_database():
    """
    Creates all necessary database tables and triggers if they don't already exist.
    This function is typically called once when the application starts.
    """
    logger.info(f"Initializing database at {DATABASE_PATH}...")
    conn = get_db_connection()  # Get a database connection.
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands.
    try:
        # --- Table Creation ---
        # SQL statements use "CREATE TABLE IF NOT EXISTS" to avoid errors if tables already exist.

        # Customers table: Stores information about customers.
        # - id: Primary key, auto-incrementing integer.
        # - name: Customer's name, cannot be null.
        # - address, phone, email: Optional contact details. Phone and email are unique.
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT UNIQUE,
            email TEXT UNIQUE
        );
        """
        )
        logger.debug("Customers table checked/created.")

        # Products table: Stores information about products.
        # - purchase_price and selling_price must be non-negative.
        # - quantity_in_stock defaults to 0 and must be non-negative.
        # - name: Product name, must be unique.
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT,
            purchase_price REAL NOT NULL CHECK(purchase_price >= 0),
            selling_price REAL NOT NULL CHECK(selling_price >= 0),
            quantity_in_stock INTEGER NOT NULL DEFAULT 0 CHECK(quantity_in_stock >= 0)
        );
        """
        )
        logger.debug("Products table checked/created.")

        # Purchases table: Records product purchases from suppliers.
        # - product_id: Foreign key referencing Products table. If a product is deleted, related purchases are also deleted (ON DELETE CASCADE).
        # - quantity and cost_per_unit must be positive.
        # - purchase_date: Stored as ISO8601 text.
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            purchase_date TEXT NOT NULL, -- ISO8601 format "YYYY-MM-DD HH:MM:SS"
            cost_per_unit REAL NOT NULL CHECK(cost_per_unit >= 0),
            supplier TEXT,
            FOREIGN KEY (product_id) REFERENCES Products(id) ON DELETE CASCADE
        );
        """
        )
        logger.debug("Purchases table checked/created.")

        # Sales table: Records sales transactions.
        # - customer_id: Foreign key referencing Customers. If a customer is deleted, their ID in sales becomes NULL (ON DELETE SET NULL).
        # - total_amount must be non-negative.
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            sale_date TEXT NOT NULL, -- ISO8601 format "YYYY-MM-DD HH:MM:SS"
            total_amount REAL NOT NULL CHECK(total_amount >= 0),
            FOREIGN KEY (customer_id) REFERENCES Customers(id) ON DELETE SET NULL
        );
        """
        )
        logger.debug("Sales table checked/created.")

        # SaleItems table: Links products to sales, detailing items in each sale.
        # - sale_id: Foreign key to Sales. If a sale is deleted, its items are also deleted (ON DELETE CASCADE).
        # - product_id: Foreign key to Products. Prevents deleting a product if it's part of any sale (ON DELETE RESTRICT).
        # - quantity and price_at_sale must be positive.
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS SaleItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            price_at_sale REAL NOT NULL CHECK(price_at_sale >= 0),
            FOREIGN KEY (sale_id) REFERENCES Sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES Products(id) ON DELETE RESTRICT -- Prevent deleting product if in sale
        );
        """
        )
        logger.debug("SaleItems table checked/created.")

        # --- Triggers ---
        # Triggers are database operations that automatically execute in response to certain events (INSERT, UPDATE, DELETE).

        # Trigger to automatically increase product stock when a new purchase is recorded.
        # - AFTER INSERT ON Purchases: Runs after a row is inserted into the Purchases table.
        # - NEW.quantity and NEW.product_id refer to the values from the newly inserted row.
        cursor.execute(
            """
        CREATE TRIGGER IF NOT EXISTS increase_stock_on_purchase
        AFTER INSERT ON Purchases
        BEGIN
            UPDATE Products
            SET quantity_in_stock = quantity_in_stock + NEW.quantity
            WHERE id = NEW.product_id;
        END;
        """
        )
        logger.debug("Trigger 'increase_stock_on_purchase' checked/created.")

        # Trigger to automatically decrease product stock when a sale item is recorded.
        # - AFTER INSERT ON SaleItems: Runs after a row is inserted into the SaleItems table.
        cursor.execute(
            """
        CREATE TRIGGER IF NOT EXISTS decrease_stock_on_sale
        AFTER INSERT ON SaleItems
        BEGIN
            UPDATE Products
            SET quantity_in_stock = quantity_in_stock - NEW.quantity
            WHERE id = NEW.product_id;
            -- Optional: Add a check here to prevent stock from going negative if not handled by UI/app logic
            -- For example, by raising an error if NEW.quantity > (SELECT quantity_in_stock FROM Products WHERE id = NEW.product_id)
            -- However, this check should ideally be done BEFORE inserting into SaleItems.
        END;
        """
        )
        logger.debug("Trigger 'decrease_stock_on_sale' checked/created.")

        # --- Indexes for Performance ---
        # Indexes help speed up data retrieval operations (SELECT queries), especially on large tables.
        # "CREATE INDEX IF NOT EXISTS" avoids errors if indexes already exist.
        indexes = {
            "idx_product_name": "CREATE INDEX IF NOT EXISTS idx_product_name ON Products(name);",
            "idx_product_category": "CREATE INDEX IF NOT EXISTS idx_product_category ON Products(category);",
            "idx_customer_name": "CREATE INDEX IF NOT EXISTS idx_customer_name ON Customers(name);",
            "idx_saleitems_sale_id": "CREATE INDEX IF NOT EXISTS idx_saleitems_sale_id ON SaleItems(sale_id);",
            "idx_saleitems_product_id": "CREATE INDEX IF NOT EXISTS idx_saleitems_product_id ON SaleItems(product_id);",
            "idx_purchases_product_id": "CREATE INDEX IF NOT EXISTS idx_purchases_product_id ON Purchases(product_id);",
            "idx_sales_customer_id": "CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON Sales(customer_id);",
            "idx_sales_sale_date": "CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON Sales(sale_date);",
        }
        for idx_name, idx_sql in indexes.items():
            cursor.execute(idx_sql)
            logger.debug(f"Index '{idx_name}' checked/created.")

        conn.commit()  # Save all changes to the database.
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        conn.rollback()  # Rollback changes if any error occurs during initialization.
        logger.error(f"Error initializing database: {e}")
        raise DatabaseError(f"Database initialization failed: {e}")
    finally:
        conn.close()  # Always close the connection.


# --- Customer Management ---
# Each function is decorated with @handle_db_error to centralize SQLite error handling.


@handle_db_error
def add_customer(name, phone=None, email=None, address=None):
    """
    Adds a new customer to the database after validating input data.
    Returns the ID of the newly added customer.
    """
    # Validate customer data using functions from 'utils.validators'.
    name, phone, email = validate_customer_data(name, phone, email)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # SQL INSERT statement to add a new row to the Customers table.
        # Placeholders (?) are used to prevent SQL injection vulnerabilities.
        cursor.execute(
            "INSERT INTO Customers (name, address, phone, email) VALUES (?, ?, ?, ?)",
            (name, address, phone, email),
        )
        conn.commit()  # Save the changes.
        customer_id = cursor.lastrowid  # Get the ID of the newly inserted row.
        logger.info(f"Customer '{name}' (ID: {customer_id}) added successfully.")
        return customer_id
    finally:
        conn.close()


@handle_db_error
def get_all_customers():
    """
    Retrieves all customers from the database, ordered by name (case-insensitive).
    Returns a list of customer records.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Selects specified columns from all rows in Customers, ordered by name.
        # COLLATE NOCASE ensures case-insensitive sorting.
        cursor.execute(
            "SELECT id, name, address, phone, email FROM Customers ORDER BY name COLLATE NOCASE"
        )
        customers = cursor.fetchall()  # Fetch all rows from the query result.
        logger.debug(f"Retrieved {len(customers)} customers.")
        return customers
    finally:
        conn.close()


@handle_db_error
def update_customer(customer_id, name, phone=None, email=None, address=None):
    """
    Updates an existing customer's details in the database.
    Requires customer_id and validates other data.
    Returns True if the update was successful.
    """
    validate_required(customer_id, "Customer ID")  # Ensure customer_id is provided.
    name, phone, email = validate_customer_data(name, phone, email)  # Validate data.

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # SQL UPDATE statement to modify an existing row.
        cursor.execute(
            """UPDATE Customers
               SET name = ?, address = ?, phone = ?, email = ?
               WHERE id = ?""",
            (name, address, phone, email, customer_id),
        )
        conn.commit()
        if cursor.rowcount == 0:  # Check if any row was actually updated.
            logger.warning(
                f"Attempted to update non-existent customer ID: {customer_id}"
            )
            raise DatabaseError(f"Customer with ID {customer_id} not found for update.")
        logger.info(f"Customer ID {customer_id} updated successfully.")
        return True
    finally:
        conn.close()


@handle_db_error
def delete_customer(customer_id):
    """
    Deletes a customer from the database by their ID.
    Returns True if deletion was successful, False otherwise.
    """
    validate_required(customer_id, "Customer ID")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # SQL DELETE statement to remove a row.
        cursor.execute("DELETE FROM Customers WHERE id = ?", (customer_id,))
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(
                f"Attempted to delete non-existent customer ID: {customer_id}"
            )
            return False  # Return False if no customer was found with that ID.
        logger.info(f"Customer ID {customer_id} deleted successfully.")
        return True
    finally:
        conn.close()


# --- Product Management ---


@handle_db_error
def add_product(
    name,
    description=None,
    category=None,
    purchase_price=0.0,
    selling_price=0.0,
    initial_stock=0,
):
    """
    Adds a new product to the database after validation.
    Category is now a required field.
    Returns the ID of the newly added product.
    """
    # Validate product data.
    name, purchase_price, selling_price, initial_stock = validate_product_data(
        name, purchase_price, selling_price, initial_stock
    )
    validate_required(category, "Product category")  # Category validation.

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO Products (name, description, category, purchase_price, selling_price, quantity_in_stock)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, description, category, purchase_price, selling_price, initial_stock),
        )
        conn.commit()
        product_id = cursor.lastrowid
        logger.info(f"Product '{name}' (ID: {product_id}) added successfully.")
        return product_id
    finally:
        conn.close()


@handle_db_error
def get_all_products():
    """
    Retrieves all products from the database, ordered by name (case-insensitive).
    Returns a list of product records.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, description, category, purchase_price, selling_price, quantity_in_stock FROM Products ORDER BY name COLLATE NOCASE"
        )
        products = cursor.fetchall()
        logger.debug(f"Retrieved {len(products)} products.")
        return products
    finally:
        conn.close()


@handle_db_error
def get_product_by_id(product_id):
    """
    Retrieves a single product from the database by its ID.
    Returns the product record or None if not found.
    """
    validate_required(product_id, "Product ID")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
        product = cursor.fetchone()  # Fetch a single row.
        if not product:
            logger.warning(f"Product with ID {product_id} not found.")
        return product
    finally:
        conn.close()


@handle_db_error
def update_product(
    product_id,
    name,
    description=None,
    category=None,
    purchase_price=0.0,
    selling_price=0.0,
):
    """
    Updates an existing product's details. Stock quantity is not updated by this function.
    Category is required. Returns True if successful.
    """
    validate_required(product_id, "Product ID")
    name, purchase_price, selling_price, _ = validate_product_data(
        name, purchase_price, selling_price, quantity=None  # Stock not updated here.
    )
    validate_required(category, "Product category")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE Products
               SET name = ?, description = ?, category = ?, purchase_price = ?, selling_price = ?
               WHERE id = ?""",
            (name, description, category, purchase_price, selling_price, product_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Attempted to update non-existent product ID: {product_id}")
            raise DatabaseError(f"Product with ID {product_id} not found for update.")
        logger.info(f"Product ID {product_id} ('{name}') updated successfully.")
        return True
    finally:
        conn.close()


@handle_db_error
def delete_product(product_id):
    """
    Deletes a product from the database by its ID.
    Returns True if successful, False otherwise.
    Note: Deletion might be restricted by foreign key constraints (e.g., if product is in SaleItems).
    """
    validate_required(product_id, "Product ID")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Attempted to delete non-existent product ID: {product_id}")
            return False
        logger.info(f"Product ID {product_id} deleted successfully.")
        return True
    finally:
        conn.close()


@handle_db_error
def search_products(query="", category_filter=None):
    """
    Searches for products by name or description (case-insensitive).
    Can also filter by a specific category.
    Returns a list of matching product records.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = "SELECT id, name, description, category, purchase_price, selling_price, quantity_in_stock FROM Products WHERE 1=1"
        params = []  # List to hold parameters for the SQL query.

        if query:  # If a search query is provided.
            sql += (
                " AND (LOWER(name) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?))"
            )
            params.extend(
                [f"%{query}%", f"%{query}%"]
            )  # Add wildcard % for partial matching.

        if (
            category_filter and category_filter != "Toutes les catégories"
        ):  # If a category filter is active.
            sql += " AND category = ?"
            params.append(category_filter)

        sql += " ORDER BY name COLLATE NOCASE"  # Always order results.
        cursor.execute(sql, params)
        products = cursor.fetchall()
        logger.debug(
            f"Search for '{query}' in category '{category_filter}' found {len(products)} products."
        )
        return products
    finally:
        conn.close()


@handle_db_error
def get_all_categories():
    """
    Retrieves a list of unique product categories from the Products table.
    Returns a list of category names.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Select distinct, non-null, non-empty categories.
        cursor.execute(
            "SELECT DISTINCT category FROM Products WHERE category IS NOT NULL AND category != '' ORDER BY category COLLATE NOCASE"
        )
        categories = [
            row["category"] for row in cursor.fetchall()
        ]  # Extract category names from rows.
        logger.debug(f"Retrieved {len(categories)} unique categories.")
        return categories
    finally:
        conn.close()


# --- Purchase Management ---


@handle_db_error
def add_purchase(
    product_id, quantity, cost_per_unit, supplier=None, purchase_date_str=None
):
    """
    Records a new product purchase.
    Stock quantity is updated automatically by the 'increase_stock_on_purchase' trigger.
    Returns the ID of the new purchase record.
    """
    validate_required(product_id, "Product ID for purchase")
    quantity = validate_numeric(
        quantity, "Purchase quantity", min_value=1  # Quantity must be at least 1.
    )
    cost_per_unit = validate_numeric(cost_per_unit, "Cost per unit", min_value=0)

    if (
        purchase_date_str is None
    ):  # If no date string is provided, use current date/time.
        purchase_date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # TODO: Add validation for purchase_date_str format if it's user-provided.

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO Purchases (product_id, quantity, purchase_date, cost_per_unit, supplier)
               VALUES (?, ?, ?, ?, ?)""",
            (product_id, quantity, purchase_date_str, cost_per_unit, supplier),
        )
        conn.commit()
        purchase_id = cursor.lastrowid
        logger.info(
            f"Purchase ID {purchase_id} recorded for product ID {product_id}, quantity {quantity}."
        )
        return purchase_id
    finally:
        conn.close()


@handle_db_error
def get_purchase_history(limit=100):
    """
    Retrieves recent purchase history, joining with product names for display.
    Limited by 'limit' parameter (default 100).
    Returns a list of purchase history records.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # SQL query to join Purchases with Products to get product names.
        cursor.execute(
            """
            SELECT p.id, p.purchase_date, pr.name AS product_name, p.quantity, p.cost_per_unit, p.supplier
            FROM Purchases p
            JOIN Products pr ON p.product_id = pr.id
            ORDER BY p.purchase_date DESC
            LIMIT ?
            """,
            (limit,),  # Parameter for LIMIT clause.
        )
        purchases = cursor.fetchall()
        logger.debug(
            f"Retrieved {len(purchases)} purchase history records (limit {limit})."
        )
        return purchases
    finally:
        conn.close()


# --- Sale Management ---


@handle_db_error
def add_sale(sale_items, customer_id=None, sale_date_str=None):
    """
    Records a new sale and its associated items.
    This function uses a transaction to ensure all or no changes are made (atomicity).
    Stock quantity is updated automatically by the 'decrease_stock_on_sale' trigger.
    Returns the ID of the new sale.
    """
    if not sale_items:  # A sale must have at least one item.
        logger.error("add_sale called with no items.")
        raise ValidationError("Cannot record a sale with no items.")

    if sale_date_str is None:  # Default to current date/time if not provided.
        sale_date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # TODO: Add validation for sale_date_str format.

    total_amount = 0  # Calculate total amount from sale items.
    for item in sale_items:
        validate_required(item.get("product_id"), "Product ID in sale item")
        item_qty = validate_numeric(
            item.get("quantity"), "Quantity in sale item", min_value=1
        )
        item_price = validate_numeric(
            item.get("price_at_sale"), "Price in sale item", min_value=0
        )
        total_amount += item_qty * item_price

    validate_numeric(
        total_amount, "Total sale amount", min_value=0  # Validate the calculated total.
    )

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")  # Start a database transaction.

        # 1. Insert into Sales table.
        cursor.execute(
            "INSERT INTO Sales (customer_id, sale_date, total_amount) VALUES (?, ?, ?)",
            (customer_id, sale_date_str, total_amount),
        )
        sale_id = cursor.lastrowid  # Get the ID of the new sale.
        if not sale_id:
            raise DatabaseError("Failed to get sale_id after Sales insert.")

        # 2. Insert each item into SaleItems table.
        for item in sale_items:
            # Optional: Check stock availability here before inserting,
            # though the trigger handles decrement and CHECK constraint on Products.quantity_in_stock
            # should prevent it from going negative if properly defined (or UI should prevent this state).
            # product_stock_info = get_product_by_id(item["product_id"])
            # if product_stock_info and item["quantity"] > product_stock_info["quantity_in_stock"]:
            #    raise ValidationError(f"Not enough stock for product ID {item['product_id']}. Available: {product_stock_info['quantity_in_stock']}, Requested: {item['quantity']}")

            cursor.execute(
                """INSERT INTO SaleItems (sale_id, product_id, quantity, price_at_sale)
                   VALUES (?, ?, ?, ?)""",
                (sale_id, item["product_id"], item["quantity"], item["price_at_sale"]),
            )
        conn.commit()  # Commit the transaction if all operations are successful.
        logger.info(
            f"Sale ID {sale_id} recorded successfully with {len(sale_items)} item(s). Total: {total_amount}"
        )
        return sale_id
    except Exception as e:  # Catch any exception during the transaction.
        conn.rollback()  # Rollback all changes if an error occurs.
        logger.error(
            f"Error during sale transaction for items {sale_items}: {e}. Transaction rolled back."
        )
        # Re-raise the original error if it's a known type, or a general DatabaseError.
        if isinstance(e, (ValidationError, DatabaseError)):
            raise
        raise DatabaseError(f"Sale recording failed: {e}")
    finally:
        conn.close()


@handle_db_error
def get_sales_history(limit=100):
    """
    Retrieves recent sales history, joining with customer names for display.
    Limited by 'limit' parameter.
    Returns a list of sale history records.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # LEFT JOIN with Customers to include sales even if customer_id is NULL (anonymous sale).
        cursor.execute(
            """
            SELECT s.id, s.sale_date, c.name AS customer_name, s.total_amount
            FROM Sales s
            LEFT JOIN Customers c ON s.customer_id = c.id
            ORDER BY s.sale_date DESC
            LIMIT ?
            """,
            (limit,),
        )
        sales = cursor.fetchall()
        logger.debug(f"Retrieved {len(sales)} sales history records (limit {limit}).")
        return sales
    finally:
        conn.close()


@handle_db_error
def get_sale_items(sale_id):
    """
    Retrieves all items associated with a specific sale ID.
    Joins with Products table to get product names.
    Returns a list of sale item records.
    """
    validate_required(sale_id, "Sale ID")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT si.id, si.product_id, p.name AS product_name, si.quantity, si.price_at_sale
            FROM SaleItems si
            JOIN Products p ON si.product_id = p.id
            WHERE si.sale_id = ?
            ORDER BY p.name COLLATE NOCASE
            """,
            (sale_id,),
        )
        items = cursor.fetchall()
        logger.debug(f"Retrieved {len(items)} items for sale ID {sale_id}.")
        return items
    finally:
        conn.close()


@handle_db_error
def get_sales_by_customer(customer_id):
    """
    Retrieves sales history for a specific customer by their ID.
    Returns a list of sales records for that customer.
    """
    validate_required(customer_id, "Customer ID")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, sale_date, total_amount
            FROM Sales
            WHERE customer_id = ?
            ORDER BY sale_date DESC
            """,
            (customer_id,),
        )
        sales = cursor.fetchall()
        logger.debug(f"Retrieved {len(sales)} sales for customer ID {customer_id}.")
        return sales
    finally:
        conn.close()


# --- Dashboard Analytics ---
# These functions provide data for the dashboard view.


@handle_db_error
def get_monthly_sales_trend(num_months=12):
    """
    Retrieves total sales amount grouped by month for the last 'num_months'.
    Used for generating sales trend charts on the dashboard.
    Returns a list of (sale_month, monthly_total) tuples.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # SQL query to group sales by month and sum total_amount.
        # strftime('%Y-%m', sale_date) extracts year and month.
        # date('now', '-X months') calculates a date X months ago.
        query = """
            SELECT
                strftime('%Y-%m', sale_date) AS sale_month,
                SUM(total_amount) AS monthly_total
            FROM Sales
            WHERE date(sale_date) >= date('now', '-' || CAST(? AS TEXT) || ' months') 
            GROUP BY sale_month
            ORDER BY sale_month ASC;
        """
        cursor.execute(query, (num_months,))
        trend_data = cursor.fetchall()
        logger.debug(
            f"Fetched monthly sales trend for last {num_months} months: {len(trend_data)} data points."
        )
        return [(row["sale_month"], row["monthly_total"]) for row in trend_data]
    finally:
        conn.close()


@handle_db_error
def get_top_selling_products(limit=5):
    """
    Retrieves the top selling products based on total quantity sold.
    Used for dashboard charts.
    Returns a list of (product_name, total_quantity_sold) tuples.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Query to sum quantities from SaleItems, grouped by product.
        query = """
            SELECT
                p.name AS product_name,
                SUM(si.quantity) AS total_quantity_sold
            FROM SaleItems si
            JOIN Products p ON si.product_id = p.id
            GROUP BY si.product_id, p.name
            ORDER BY total_quantity_sold DESC
            LIMIT ?;
        """
        cursor.execute(query, (limit,))
        top_products = cursor.fetchall()
        logger.debug(
            f"Fetched top {limit} selling products: {len(top_products)} products."
        )
        return [
            (row["product_name"], row["total_quantity_sold"]) for row in top_products
        ]
    finally:
        conn.close()


# --- Product details for sale ---
@handle_db_error
def get_product_details_for_sale(product_id):
    """
    Fetch product details for a given product ID, including name, price, and stock.

    Args:
        product_id (int): The ID of the product to fetch details for.

    Returns:
        dict: A dictionary containing product details (name, price, stock) or None if not found.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT name, selling_price, quantity_in_stock
            FROM Products
            WHERE id = ?
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "name": result[0],
                "price": result[1],
                "stock": result[2],
            }
        else:
            return None
    except sqlite3.Error as e:
        logger.error(f"Error fetching product details for sale: {e}")
        return None


# --- Main block for direct execution (e.g., for initializing the DB) ---
if __name__ == "__main__":
    # This block is executed if the script is run directly (e.g., 'python database.py').
    # It's useful for initial setup or testing database functions.
    # For this to work standalone, 'utils.error_handler' and 'utils.validators'
    # need to be accessible in the PYTHONPATH.

    # Basic logger setup if this script is run directly (usually done in the main app).
    if not logging.getLogger("inventory_app").hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,  # Show detailed logs for direct execution.
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    logger.info(
        f"Database script executed directly. Initializing database at: {DATABASE_PATH}"
    )
    try:
        initialize_database()  # Call the initialization function.
        # --- Example Usage (Optional, for testing during direct execution) ---
        # Uncomment these lines to test functions after initialization.
        # logger.info("Testing database functions...")
        # if not get_all_customers():
        #     add_customer("Test Customer", "1234567890", "test@example.com", "1 Test St")
        # if not get_all_products():
        #     add_product("Test Product", "A test product", "Test Category", 10.0, 20.0, 50)

        # customers = get_all_customers()
        # logger.info(f"Found {len(customers)} customers.")
        # products = get_all_products()
        # logger.info(f"Found {len(products)} products.")

    except DatabaseError as e:
        logger.critical(
            f"Failed to initialize or access database during direct execution: {e}"
        )


@handle_db_error
def dangerously_delete_all_data():
    """
    Deletes all data from all tables by dropping them and re-initializing the database.
    This is a highly destructive operation.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        logger.warning("Starting deletion of all data by dropping tables.")
        tables_to_drop = [
            "SaleItems",
            "Sales",
            "Purchases",
            "Products",
            "Customers",
        ]  # Order might matter due to FKs if not dropping all

        # It's often easier and cleaner to just delete the DB file and reinitialize,
        # or drop tables in an order that respects foreign keys, or disable FK checks temporarily.
        # For simplicity and to ensure a clean slate including schema reset, re-initialization is good.

        # Option 1: Close connection, delete file, reinitialize (simplest for full reset)
        conn.close()  # Close current connection
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            logger.info(f"Database file '{DATABASE_PATH}' removed.")
        else:
            logger.warning(
                f"Database file '{DATABASE_PATH}' not found for deletion, will reinitialize."
            )

        initialize_database()  # This will recreate the DB file and all tables/triggers
        logger.info("Database has been re-initialized after deleting all data.")

        # Option 2: Drop tables individually (more complex if FKs are strict and not CASCADE)
        # conn.execute("PRAGMA foreign_keys = OFF;") # Temporarily disable FK for dropping
        # for table in tables_to_drop:
        #     logger.info(f"Dropping table {table}...")
        #     cursor.execute(f"DROP TABLE IF EXISTS {table}")
        # conn.commit()
        # logger.info("All application tables dropped.")
        # conn.execute("PRAGMA foreign_keys = ON;")
        # initialize_database() # Recreate tables and triggers

        return True
    except Exception as e:
        # conn.rollback() # Not needed if re-creating file
        logger.error(f"Error during dangerously_delete_all_data: {e}", exc_info=True)
        raise DatabaseError(f"Failed to delete all data: {str(e)}")
    # finally:
    # conn.close() # Already closed if using option 1, or should be closed if option 2 used fully.
