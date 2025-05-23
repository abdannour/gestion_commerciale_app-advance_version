# Updated content for sidou2/views/sale_view.py
import sys  # Provides access to system-specific parameters and functions, e.g., for running the app.
import datetime  # Standard library for working with dates and times.
from PyQt6.QtWidgets import (  # Import necessary UI components from PyQt6.
    QWidget,  # Base class for all UI objects.
    QVBoxLayout,  # Arranges widgets vertically.
    QHBoxLayout,  # Arranges widgets horizontally.
    QLabel,  # Displays text or images.
    QPushButton,  # Command button.
    QTableWidget,  # For displaying data in a grid.
    QTableWidgetItem,  # Represents a cell in a QTableWidget.
    QMessageBox,  # For showing pop-up messages (alerts, warnings, info).
    QHeaderView,  # Provides headers for item views like QTableWidget.
    QAbstractItemView,  # Base class for item views.
    QComboBox,  # Dropdown list for selecting items.
    QSpinBox,  # For inputting integer values with up/down buttons.
    QGridLayout,  # Arranges widgets in a grid.
    QGroupBox,  # Provides a framed box with a title, used for grouping widgets.
    QDialog,  # Base class for dialog windows.
    QDialogButtonBox,  # Provides a standard layout for dialog buttons (OK, Cancel, etc.).
    QTextEdit,  # For displaying and editing multi-line rich text.
    QFrame,  # Provides a frame, often used as a container or for styling.
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)  # Import core Qt functionalities, including signals for custom communication.
from PyQt6.QtGui import QFont  # Import classes for graphical elements like fonts.

# --- Local Module Imports ---
# Import database interaction functions.
from database.database import (
    add_sale,  # Function to record a new sale in the database.
    get_sales_history,  # Function to retrieve past sales records.
    get_sale_items,  # Function to get all items associated with a specific sale.
    get_all_products,  # Function to fetch all products from the database.
    get_all_customers,  # Function to fetch all customers from the database.
    get_product_by_id,  # Function to retrieve a single product by its ID.
    get_db_connection,  # Function to establish a database connection.
    get_product_details_for_sale,  # Function to fetch product details (name, price, stock) for sale.
)

# Import theme-related variables and functions for consistent styling.
from theme import STYLES, COLORS, FONTS, SPACING, RADIUS

# Import custom error handler for database-related exceptions.
from utils.error_handler import DatabaseError

# Import the BaseView class, which provides common functionalities for all views.
from views.base_view import BaseView


class SaleView(
    BaseView
):  # Main class for the sales management view, inheriting from BaseView.
    """
    Manages the user interface for sales operations, including creating new sales,
    viewing sales history, and displaying sale details and receipts.
    It interacts with the database to fetch and record sales data.
    """

    # Define a custom signal that is emitted when a new sale is successfully recorded.
    # This can be used to notify other parts of the application (e.g., to refresh data).
    sale_recorded = pyqtSignal()

    def __init__(self):  # Constructor for the SaleView.
        """
        Initializes the SaleView, sets up caches for products and customers,
        and prepares UI elements and initial data.
        """
        super().__init__(
            "Gestion des Ventes"
        )  # Call the constructor of the BaseView with the title for this view.
        self.products_cache = (
            {}
        )  # Cache to store product data (ID -> {name, price, stock}) for quick access.
        self.customers_cache = {}  # Cache to store customer data (ID -> name).
        self.current_sale_items = (
            []
        )  # List to hold items currently added to the new sale (the cart).
        self.selected_sale_id_for_details = None  # Stores the ID of a sale selected from the history table for viewing details.
        self._init_ui_elements()  # Initialize the user interface elements specific to this view.
        self.load_initial_data()  # Load initial data required for the view (products, customers, sales history).

    def _init_ui_elements(
        self,
    ):  # Renamed from init_ui to avoid potential clashes if BaseView had its own.
        """
        Sets up the primary UI layout and all interactive elements for the SaleView.
        This includes sections for creating a new sale and viewing sales history.
        """
        self.create_title()  # Use BaseView's method to create and add the main title label.

        # Main layout for the SaleView will be horizontal, splitting space between new sale and history sections.
        main_layout = QHBoxLayout()  # <-- FIX: do not parent to self
        main_layout.setContentsMargins(  # Set margins around the main layout using theme spacing.
            int(SPACING["lg"].replace("px", "")),  # Left margin.
            int(SPACING["lg"].replace("px", "")),  # Top margin.
            int(SPACING["lg"].replace("px", "")),  # Right margin.
            int(SPACING["lg"].replace("px", "")),  # Bottom margin.
        )
        main_layout.setSpacing(
            int(SPACING["lg"].replace("px", ""))
        )  # Set spacing between child widgets/layouts.

        # --- "Nouvelle Vente" (New Sale) Section ---
        # GroupBox to visually group elements related to creating a new sale.
        new_sale_group = QGroupBox("Nouvelle Vente")  # Title for the group box.
        new_sale_group.setStyleSheet(
            STYLES.get("group_box", "")
        )  # Apply themed styling to the GroupBox.
        new_sale_layout = QVBoxLayout(
            new_sale_group
        )  # Vertical layout for content inside the new_sale_group.
        new_sale_layout.setSpacing(
            int(SPACING["md"].replace("px", ""))
        )  # Spacing for elements within this group.

        # Customer selection area.
        customer_layout = (
            QHBoxLayout()
        )  # Horizontal layout for customer label and combobox.
        customer_label = QLabel("Client:")  # Label for customer selection.
        self.customer_combo = QComboBox()  # Dropdown to select a customer for the sale.
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_combo)
        new_sale_layout.addLayout(
            customer_layout
        )  # Add customer selection to the new sale layout.

        # Area for adding items (product, quantity) to the current sale.
        add_item_layout = (
            QGridLayout()
        )  # Grid layout for better arrangement of product, quantity, price, stock.
        add_item_layout.setSpacing(int(SPACING["sm"].replace("px", "")))
        product_label = QLabel("Produit:")  # Label for product selection.
        self.product_combo = QComboBox()  # Dropdown to select a product.
        # Connect the product selection change to update displayed price and stock.
        self.product_combo.currentIndexChanged.connect(
            self.update_price_and_stock_display
        )
        quantity_label = QLabel("Qté:")  # Label for quantity input.
        self.quantity_spinbox = QSpinBox()  # Spinbox for entering product quantity.
        self.quantity_spinbox.setRange(
            1, 1
        )  # Initial range, will be updated based on stock.

        # Add product and quantity widgets to the grid layout.
        add_item_layout.addWidget(product_label, 0, 0)  # Row 0, Col 0.
        add_item_layout.addWidget(
            self.product_combo, 0, 1, 1, 3
        )  # Row 0, Col 1, spans 1 row and 3 columns for wider product name display.
        add_item_layout.addWidget(
            quantity_label, 1, 0
        )  # Row 1, Col 0 (Quantity on a new line for clarity).
        add_item_layout.addWidget(self.quantity_spinbox, 1, 1)  # Row 1, Col 1.

        # Labels to display the unit price and available stock of the selected product.
        self.price_display_label = QLabel(
            "Prix Unit.: --.-- DZD"
        )  # Placeholder for price.
        self.price_display_label.setStyleSheet(  # Styling for the price display.
            f"font-weight: bold; color: {COLORS.get('text_secondary', '#4f46e5')}; font-size: {FONTS['sm']}pt;"
        )
        add_item_layout.addWidget(
            self.price_display_label,
            1,
            2,
            Qt.AlignmentFlag.AlignRight,  # Row 1, Col 2, aligned right.
        )

        self.stock_display_label = QLabel(
            "Stock: --"
        )  # Placeholder for stock quantity.
        self.stock_display_label.setStyleSheet(  # Styling for the stock display.
            f"font-weight: bold; color: {COLORS.get('text_secondary', '#4f46e5')}; font-size: {FONTS['sm']}pt;"
        )
        add_item_layout.addWidget(
            self.stock_display_label,
            1,
            3,
            Qt.AlignmentFlag.AlignRight,  # Row 1, Col 3, aligned right.
        )

        # Button to add the selected product and quantity to the current sale cart.
        self.add_item_button = (
            self.create_button(  # Use BaseView's helper to create a themed button.
                "➕ Ajouter au Panier",
                self.add_item_to_sale,
                style_key="button_primary",
            )
        )
        self.add_item_button.setMinimumHeight(40)  # Set minimum height for the button.
        add_item_layout.addWidget(
            self.add_item_button, 2, 0, 1, 4
        )  # Row 2, Col 0, spans 4 columns.
        new_sale_layout.addLayout(
            add_item_layout
        )  # Add the item addition layout to the new sale group.

        # Apply styles to input fields and labels within the new_sale_group using BaseView methods.
        for widget in [customer_label, product_label, quantity_label]:
            widget.setStyleSheet(STYLES.get("label", ""))  # Apply standard label style.
        for widget in [self.customer_combo, self.product_combo, self.quantity_spinbox]:
            widget.setStyleSheet(
                STYLES.get("input", "")
            )  # Apply standard input field style.
            widget.setMinimumHeight(35)  # Ensure consistent height for input fields.

        # "Panier Actuel" (Current Cart) section.
        cart_label = QLabel("Panier Actuel:")  # Label for the current sale items table.
        cart_label.setStyleSheet(
            STYLES.get("label_bold", "")
        )  # Apply bold label style.
        new_sale_layout.addWidget(cart_label)

        # Table to display items added to the current sale (the cart).
        self.current_sale_table = (
            self.create_table(  # Use BaseView's helper to create a themed table.
                [
                    "Produit",
                    "Qté",
                    "Prix Unit.",
                    "Sous-Total",
                    "Retirer",
                ]  # Column headers.
            )
        )
        # Configure column resizing behavior.
        self.current_sale_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch  # Stretch columns to fill available width.
        )
        self.current_sale_table.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents,  # "Retirer" column resizes to content.
        )
        new_sale_layout.addWidget(
            self.current_sale_table
        )  # Add cart table to the new sale group.

        # Layout for total amount display and finalize/clear sale buttons.
        finalize_layout = QHBoxLayout()
        finalize_layout.setSpacing(int(SPACING["md"].replace("px", "")))
        self.total_label = QLabel(
            "Total Vente: 0.00 DZD"
        )  # Label to display the total amount of the current sale.
        self.total_label.setStyleSheet(  # Styling for the total label.
            STYLES.get(
                "subtitle",  # Use subtitle style from theme.
                # Fallback style if "subtitle" is not in STYLES:
                f"font-weight: bold; font-size: {FONTS['lg']}pt; color: {COLORS['text_primary']};",
            )
        )

        # Button to clear all items from the current sale cart and reset inputs.
        self.clear_sale_button = self.create_button(
            "❌ Annuler Vente",
            self.clear_current_sale,
            style_key="button_destructive",  # Destructive action style.
        )
        self.clear_sale_button.setMinimumHeight(40)

        # Button to finalize the current sale and record it in the database.
        self.finalize_button = self.create_button(
            "✓ Finaliser la Vente",
            self.finalize_current_sale,
            style_key="button_success",  # Success action style.
        )
        self.finalize_button.setMinimumHeight(
            45
        )  # Make this button slightly more prominent.

        # Add total label and buttons to the finalize_layout.
        finalize_layout.addWidget(self.total_label)
        finalize_layout.addStretch()  # Add stretchable space to push buttons to the right.
        finalize_layout.addWidget(self.clear_sale_button)
        finalize_layout.addWidget(self.finalize_button)
        new_sale_layout.addLayout(
            finalize_layout
        )  # Add finalize layout to the new sale group.

        # Add the "Nouvelle Vente" group to the main horizontal layout.
        # The '2' indicates it takes twice the stretch factor compared to the history section (if history is 1).
        main_layout.addWidget(new_sale_group, 2)

        # --- "Historique des Ventes" (Sales History) Section ---
        history_group = QGroupBox(
            "Historique des Ventes"
        )  # GroupBox for sales history.
        history_group.setStyleSheet(
            STYLES.get("group_box", "")
        )  # Apply themed styling.
        history_layout = QVBoxLayout(
            history_group
        )  # Vertical layout for content inside history_group.
        history_layout.setSpacing(int(SPACING["md"].replace("px", "")))

        # Table to display past sales records.
        self.history_table = self.create_table(  # Use BaseView's helper.
            ["ID Vente", "Date", "Client", "Montant Total"]  # Column headers.
        )
        # Configure column resizing behavior.
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,  # "ID Vente" column resizes to content.
        )
        # Table properties.
        self.history_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # Make table read-only.
        self.history_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows  # Select entire rows.
        )
        self.history_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection  # Allow only one row to be selected at a time.
        )
        self.history_table.verticalHeader().setVisible(
            False
        )  # Hide vertical row numbers.
        self.history_table.itemSelectionChanged.connect(
            self.on_history_row_selected
        )  # Add this line
        history_layout.addWidget(self.history_table)  # Add history table to its group.

        # Layout for buttons related to sales history (view details, generate receipt, refresh).
        history_button_layout = QHBoxLayout()
        history_button_layout.setSpacing(int(SPACING["sm"].replace("px", "")))

        # Button to view detailed items of a selected sale from the history. Initially disabled.
        self.view_details_button = self.create_button(
            "Voir Détails",
            self.show_sale_details_dialog,  # Method to call on click.
            enabled=False,  # Disabled until a sale is selected.
            style_key="button_secondary",  # Secondary button style.
        )
        # Button to generate a receipt for a selected sale. Initially disabled.
        self.generate_receipt_button = self.create_button(
            "Générer Ticket",
            self.show_receipt_dialog,  # Method to call on click.
            enabled=False,  # Disabled until a sale is selected.
            style_key="button_secondary",
        )
        # Button to refresh the sales history table.
        self.refresh_history_button = self.create_button(
            "Rafraîchir",
            self.load_sales_history,
            style_key="button_ghost",  # Ghost button style.
        )
        # Set minimum height for these history-related buttons.
        for btn in [
            self.view_details_button,
            self.generate_receipt_button,
            self.refresh_history_button,
        ]:
            btn.setMinimumHeight(35)

        # Add buttons to the history_button_layout.
        history_button_layout.addStretch()  # Push buttons to the right.
        history_button_layout.addWidget(self.view_details_button)
        history_button_layout.addWidget(self.generate_receipt_button)
        history_button_layout.addWidget(self.refresh_history_button)
        history_layout.addLayout(
            history_button_layout
        )  # Add button layout to the history group.

        # Add the "Historique des Ventes" group to the main horizontal layout.
        # The '1' indicates it takes one part of the stretch factor.
        main_layout.addWidget(history_group, 1)

        # The main_layout (QHBoxLayout) was already added to self.main_layout (QVBoxLayout from BaseView)
        # IF self.main_layout was intended to be the QHBoxLayout directly, then this line is not needed:
        # self.main_layout.addLayout(main_layout)
        # Correction: BaseView sets self.main_layout = QVBoxLayout(self).
        # So, the QHBoxLayout `main_layout` created here should be added to BaseView's `self.main_layout`.
        self.main_layout.addLayout(main_layout)

    def load_initial_data(self):
        """
        Loads all necessary initial data when the view is first created or shown.
        This includes populating product and customer comboboxes and the sales history table.
        """
        self.load_products_for_sale()  # Populate the product selection dropdown.
        self.load_customers_for_sale()  # Populate the customer selection dropdown.
        self.load_sales_history()  # Load and display past sales.

    def load_products_for_sale(self):
        """
        Fetches all products from the database and populates the product_combo QComboBox.
        Only products with stock > 0 are shown. Caches product details for quick access.
        """
        self.product_combo.clear()  # Clear existing items.
        self.products_cache.clear()  # Clear product cache.
        self.product_combo.addItem(
            "Sélectionner un produit...", -1
        )  # Add a default placeholder item.
        try:
            products = get_all_products()  # Fetch all products from the database.
            if products:
                for product in products:
                    # Only add products that are in stock.
                    if product["quantity_in_stock"] > 0:
                        # Display product name and current stock in the combobox item text.
                        self.product_combo.addItem(
                            f"{product['name']} (Stock: {product['quantity_in_stock']})",
                            product["id"],  # Store product ID as item data.
                        )
                        # Cache essential product details.
                        self.products_cache[product["id"]] = {
                            "name": product["name"],
                            "price": product["selling_price"],
                            "stock": product["quantity_in_stock"],
                        }
            self.update_price_and_stock_display()  # Update price/stock labels for the currently selected/default product.
        except DatabaseError as e:  # Handle potential database errors.
            self.show_error(  # Use BaseView's error message display.
                "Erreur Produits",
                f"Impossible de charger les produits: {e}",
            )

    def load_customers_for_sale(self):
        """
        Fetches all customers from the database and populates the customer_combo QComboBox.
        Includes an option for anonymous sales. Caches customer names.
        """
        self.customer_combo.clear()  # Clear existing items.
        self.customers_cache.clear()  # Clear customer cache.
        self.customer_combo.addItem(
            "Vente Anonyme", -1
        )  # Default option for sales without a specific customer.
        try:
            customers = get_all_customers()  # Fetch all customers.
            if customers:
                for customer in customers:
                    self.customer_combo.addItem(
                        customer["name"], customer["id"]
                    )  # Add customer name and store ID.
                    self.customers_cache[customer["id"]] = customer[
                        "name"
                    ]  # Cache customer name.
        except Exception as e:  # Handle potential errors.
            QMessageBox.critical(  # Standard Qt MessageBox for critical errors.
                self, "Erreur Clients", f"Impossible de charger les clients: {e}"
            )

    def update_price_and_stock_display(self):
        """
        Updates the price and stock display labels based on the currently selected product
        in the product_combo. Also adjusts the range of the quantity_spinbox.
        """
        selected_index = (
            self.product_combo.currentIndex()
        )  # Get the index of the currently selected item.
        if (
            selected_index > 0
        ):  # If a product is selected (index 0 is "Sélectionner un produit...").
            product_id = self.product_combo.itemData(
                selected_index
            )  # Get the product ID stored with the item.
            if (
                product_id in self.products_cache
            ):  # Check if product details are in cache.
                product_info = self.products_cache[product_id]
                # Update labels with formatted price and stock.
                self.price_display_label.setText(
                    f"Prix Unit.: {product_info['price']:.2f} DZD"
                )
                self.stock_display_label.setText(f"Stock: {product_info['stock']}")
                # Set the quantity spinbox range from 1 to available stock.
                self.quantity_spinbox.setRange(1, product_info["stock"])
                # Enable quantity input and add button only if stock is available.
                self.quantity_spinbox.setEnabled(product_info["stock"] > 0)
                self.add_item_button.setEnabled(product_info["stock"] > 0)
            else:  # Fallback if product ID not in cache (should not happen with current logic).
                self.price_display_label.setText("Prix Unit.: --.-- DZD")
                self.stock_display_label.setText("Stock: --")
                self.quantity_spinbox.setRange(1, 1)
                self.quantity_spinbox.setEnabled(False)
                self.add_item_button.setEnabled(False)
        else:  # If no product is selected, reset labels and disable quantity/add button.
            self.price_display_label.setText("Prix Unit.: --.-- DZD")
            self.stock_display_label.setText("Stock: --")
            self.quantity_spinbox.setRange(1, 1)
            self.quantity_spinbox.setEnabled(False)
            self.add_item_button.setEnabled(False)

    def add_item_to_sale(self):
        """
        Adds the selected product with the specified quantity to the current_sale_items list (the cart).
        Validates product selection, quantity, and stock availability before adding.
        Updates the cart table and total amount.
        """
        # Get product ID from the combobox.
        selected_product_index = self.product_combo.currentIndex()
        if selected_product_index <= 0:  # Check if a product is selected.
            self.show_warning(
                "Produit Non Sélectionné", "Veuillez sélectionner un produit."
            )
            return
        product_id = self.product_combo.itemData(selected_product_index)

        # Get quantity from the spinbox.
        quantity_to_add = self.quantity_spinbox.value()
        if quantity_to_add <= 0:  # Validate quantity.
            self.show_warning(
                "Quantité Invalide", "La quantité doit être supérieure à zéro."
            )
            return

        # Retrieve product details from cache.
        if product_id not in self.products_cache:
            self.show_error("Erreur Produit", "Détails du produit non trouvés.")
            return
        product_info = self.products_cache[product_id]

        # Check stock availability (considering items already in the cart for the same product).
        current_cart_qty_for_product = 0
        for item in self.current_sale_items:
            if item["product_id"] == product_id:
                current_cart_qty_for_product = item["quantity"]
                break

        if quantity_to_add + current_cart_qty_for_product > product_info["stock"]:
            self.show_warning(
                "Stock Insuffisant",
                f"Stock insuffisant pour {product_info['name']}. "
                f"Disponible: {product_info['stock']}, Au panier: {current_cart_qty_for_product}, Demandé: {quantity_to_add}.",
            )
            return

        # Add or update item in the current_sale_items list (cart).
        found_in_cart = False
        for item in self.current_sale_items:
            if (
                item["product_id"] == product_id
            ):  # If product already in cart, update its quantity.
                item["quantity"] += quantity_to_add
                item["subtotal"] = (
                    item["quantity"] * item["price_at_sale"]
                )  # Recalculate subtotal.
                found_in_cart = True
                break

        if not found_in_cart:  # If product not in cart, add as a new item.
            self.current_sale_items.append(
                {
                    "product_id": product_id,
                    "name": product_info["name"],
                    "quantity": quantity_to_add,
                    "price_at_sale": product_info[
                        "price"
                    ],  # Price at the time of adding to cart.
                    "subtotal": quantity_to_add * product_info["price"],
                }
            )

        self.refresh_current_sale_table()  # Update the visual cart table.
        self.update_total()  # Recalculate and display the total sale amount.
        # Optionally, reset product selection and quantity input after adding.
        self.product_combo.setCurrentIndex(0)  # Reset product selection.
        self.quantity_spinbox.setValue(1)  # Reset quantity to 1.
        self.show_info_message(  # Temporary informational message (can be a status bar message).
            f"{quantity_to_add} x {product_info['name']} ajouté(s) au panier."
        )

    def refresh_current_sale_table(self):
        """
        Updates the current_sale_table QTableWidget with items from the current_sale_items list.
        Also adds a "Remove" button for each item in the cart.
        """
        self.current_sale_table.setRowCount(0)  # Clear existing rows.
        self.current_sale_table.setRowCount(
            len(self.current_sale_items)
        )  # Set row count based on cart items.
        for row_idx, item in enumerate(self.current_sale_items):
            # Populate cells with item details.
            self.current_sale_table.setItem(row_idx, 0, QTableWidgetItem(item["name"]))
            self.current_sale_table.setItem(
                row_idx, 1, QTableWidgetItem(str(item["quantity"]))
            )
            self.current_sale_table.setItem(
                row_idx,
                2,
                QTableWidgetItem(
                    f"{item['price_at_sale']:.2f} DZD"
                ),  # Formatted price.
            )
            self.current_sale_table.setItem(
                row_idx,
                3,
                QTableWidgetItem(f"{item['subtotal']:.2f} DZD"),  # Formatted subtotal.
            )
            # Create and add a "Remove" button (X) for each cart item.
            remove_button = QPushButton("X")
            remove_button.setFixedSize(25, 25)  # Small fixed size for the button.
            remove_button.setStyleSheet(  # Styling for the remove button (red, bold X).
                f"color: {COLORS.get('error', 'red')}; font-weight: bold; border: none; background-color: transparent;"
            )
            remove_button.setToolTip(
                "Retirer cet article du panier"
            )  # Tooltip for the button.
            # Connect the button's click to the remove_item_from_sale method, passing the row index.
            # Lambda function captures the row_idx at the time of button creation.
            remove_button.clicked.connect(
                lambda checked, r=row_idx: self.remove_item_from_sale(r)
            )
            self.current_sale_table.setCellWidget(
                row_idx, 4, remove_button
            )  # Add button to the last column.

        # Enable or disable the "Finalize Sale" button based on whether the cart has items.
        self.finalize_button.setEnabled(len(self.current_sale_items) > 0)

    def remove_item_from_sale(self, row_index):
        """
        Removes an item from the current_sale_items list (cart) at the given row_index.
        Updates the cart table and total amount.
        """
        if (
            0 <= row_index < len(self.current_sale_items)
        ):  # Check if the index is valid.
            del self.current_sale_items[row_index]  # Remove item from the list.
            self.refresh_current_sale_table()  # Refresh the visual cart table.
            self.update_total()  # Recalculate and update the total sale amount.

    def update_total(self):
        """
        Calculates the total amount for all items in the current_sale_items list (cart)
        and updates the total_label to display it.
        """
        total = sum(
            item["subtotal"] for item in self.current_sale_items
        )  # Sum subtotals of all cart items.
        self.total_label.setText(
            f"Total Vente: {total:.2f} DZD"
        )  # Update the display label, formatted as currency.

    def clear_current_sale(self):
        """
        Clears all items from the current sale (cart), resets input fields (customer, product, quantity),
        and updates the UI accordingly.
        """
        self.current_sale_items = []  # Empty the cart list.
        self.refresh_current_sale_table()  # Clear the visual cart table.
        self.update_total()  # Reset the total amount display to 0.00 DZD.
        # Reset input fields to their default states.
        self.customer_combo.setCurrentIndex(0)  # Select "Vente Anonyme".
        self.product_combo.setCurrentIndex(0)  # Select "Sélectionner un produit...".
        self.quantity_spinbox.setValue(1)  # Reset quantity to 1.
        self.finalize_button.setEnabled(
            False
        )  # Disable the "Finalize Sale" button as cart is empty.

    def finalize_current_sale(self):
        """
        Finalizes the current sale by recording it in the database.
        Shows a confirmation dialog before proceeding. If confirmed, it adds the sale,
        clears the cart, refreshes relevant data (history, product stock), and emits a signal.
        """
        if not self.current_sale_items:  # Check if the cart is empty.
            QMessageBox.warning(
                self, "Vente Vide", "Le panier est vide."
            )  # Show warning if cart is empty.
            return

        # Get selected customer ID (or None for anonymous).
        selected_customer_index = self.customer_combo.currentIndex()
        customer_id = (
            self.customer_combo.itemData(
                selected_customer_index
            )  # Retrieve customer ID stored with the item.
            if selected_customer_index > 0  # Index 0 is "Vente Anonyme".
            else None
        )

        # Prepare items data in the format expected by the database function add_sale.
        items_for_db = [
            {
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "price_at_sale": item["price_at_sale"],  # Price at the time of sale.
            }
            for item in self.current_sale_items
        ]
        total = sum(
            item["subtotal"] for item in self.current_sale_items
        )  # Calculate total for confirmation.
        customer_name_display = (
            self.customer_combo.currentText()
        )  # Get customer name for confirmation message.
        item_count = len(
            self.current_sale_items
        )  # Get number of items for confirmation.

        # Confirmation message for the user.
        confirm_msg = (
            f"Confirmer la vente ?\n\nClient: {customer_name_display}\n"
            f"Nombre d'articles: {item_count}\nMontant Total: {total:.2f} DZD"
        )
        # Show a confirmation dialog.
        reply = QMessageBox.question(
            self,  # Parent widget.
            "Confirmation Vente",  # Dialog title.
            confirm_msg,  # Message text.
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.Cancel,  # Buttons.
            QMessageBox.StandardButton.Cancel,  # Default selected button.
        )

        if reply == QMessageBox.StandardButton.Yes:  # If user confirms.
            try:
                # Attempt to add the sale to the database.
                sale_id = add_sale(items_for_db, customer_id)
                if sale_id:  # If sale was added successfully (returns sale ID).
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"Vente ID {sale_id} enregistrée.",  # Success message.
                    )
                    self.clear_current_sale()  # Clear the cart and reset inputs.
                    self.load_sales_history()  # Refresh the sales history table.
                    self.load_products_for_sale()  # Refresh product list (stock might have changed).
                    self.sale_recorded.emit()  # Emit signal indicating a sale was recorded.
                else:  # Should not happen if add_sale raises error or returns ID.
                    QMessageBox.critical(
                        self, "Erreur", "Erreur lors de l'enregistrement de la vente."
                    )
            except Exception as e:  # Catch any potential database or other errors.
                QMessageBox.critical(
                    self,
                    "Erreur Base de Données",
                    f"Erreur lors de l'enregistrement: {e}",
                )

    def load_sales_history(self):
        """
        Fetches sales history from the database and populates the history_table QTableWidget.
        Disables "View Details" and "Generate Receipt" buttons initially.
        """
        self.history_table.setRowCount(0)  # Clear existing rows.
        self.selected_sale_id_for_details = None  # Reset selected sale ID.
        # Disable buttons that require a selection.
        self.view_details_button.setEnabled(False)
        self.generate_receipt_button.setEnabled(False)
        try:
            history = (
                get_sales_history()
            )  # Fetch sales history (typically recent sales).
            if history:
                self.history_table.setRowCount(len(history))  # Set row count.
                for row_idx, sale in enumerate(history):
                    # Populate cells with sale data.
                    self.history_table.setItem(
                        row_idx, 0, QTableWidgetItem(str(sale["id"]))  # Sale ID.
                    )
                    date_str = sale["sale_date"]  # Sale date as string.
                    try:  # Attempt to parse and format the date for display.
                        dt_obj = datetime.datetime.fromisoformat(date_str)
                        display_date = dt_obj.strftime(
                            "%Y-%m-%d %H:%M"
                        )  # Formatted date.
                    except ValueError:  # If parsing fails, use the original string.
                        display_date = date_str
                    self.history_table.setItem(
                        row_idx, 1, QTableWidgetItem(display_date)  # Sale date.
                    )
                    self.history_table.setItem(
                        row_idx,
                        2,
                        QTableWidgetItem(
                            sale["customer_name"] or "Anonyme"
                        ),  # Customer name or "Anonyme".
                    )
                    self.history_table.setItem(
                        row_idx,
                        3,
                        QTableWidgetItem(
                            f"{sale['total_amount']:.2f} DZD"
                        ),  # Total amount, formatted.
                    )
        except Exception as e:  # Handle potential errors.
            QMessageBox.critical(
                self, "Erreur Historique", f"Impossible de charger l'historique: {e}"
            )

    def on_history_row_selected(
        self,
    ):  # Slot connected to history_table's itemSelectionChanged signal
        """
        Called when a row is selected in the sales history_table.
        Updates self.selected_sale_id_for_details and enables/disables relevant buttons.
        """
        selected_items = self.history_table.selectedItems()  # Get all selected cells.
        if selected_items:  # If any cell (and thus a row) is selected.
            selected_row = (
                self.history_table.currentRow()
            )  # Get the index of the selected row.
            # Get the sale ID from the first column of the selected row.
            self.selected_sale_id_for_details = int(
                self.history_table.item(selected_row, 0).text()
            )
            # Enable buttons now that a sale is selected.
            self.view_details_button.setEnabled(True)
            self.generate_receipt_button.setEnabled(True)
        else:  # If selection is cleared.
            self.selected_sale_id_for_details = None  # Reset selected ID.
            # Disable buttons.
            self.view_details_button.setEnabled(False)
            self.generate_receipt_button.setEnabled(False)

    def show_sale_details_dialog(self):
        """
        Displays a dialog showing the detailed items of the selected sale from the history.
        If no sale is selected, it tries to get the ID from the current row or shows a message.
        """
        if (
            self.selected_sale_id_for_details is None
        ):  # If no sale ID stored from selection event.
            current_row = (
                self.history_table.currentRow()
            )  # Check if a row is currently visually selected.
            if current_row >= 0:  # If a row is selected.
                self.selected_sale_id_for_details = int(
                    self.history_table.item(
                        current_row, 0
                    ).text()  # Get ID from that row.
                )
            else:  # No sale selected.
                QMessageBox.information(
                    self,
                    "Information",
                    "Veuillez sélectionner une vente dans l'historique.",
                )
                return  # Exit if no sale is selected.

        if self.selected_sale_id_for_details is not None:  # If a sale ID is available.
            try:
                # Fetch items for the selected sale.
                items = get_sale_items(self.selected_sale_id_for_details)
                # Create and show the SaleDetailsDialog.
                dialog = SaleDetailsDialog(
                    self.selected_sale_id_for_details,
                    items,
                    self,  # Pass sale ID, items, and parent.
                )
                dialog.exec()  # Show dialog modally.
            except (
                Exception
            ) as e:  # Handle errors during dialog creation or data fetching.
                QMessageBox.critical(
                    self, "Erreur Détails", f"Impossible de charger les détails: {e}"
                )

    def show_receipt_dialog(self):
        """
        Generates and displays a sales receipt for the selected sale in a dialog.
        If no sale is selected, it tries to get the ID from the current row or shows a message.
        """
        if (
            self.selected_sale_id_for_details is None
        ):  # Similar logic to show_sale_details_dialog for getting ID.
            current_row = self.history_table.currentRow()
            if current_row >= 0:
                self.selected_sale_id_for_details = int(
                    self.history_table.item(current_row, 0).text()
                )
            else:
                QMessageBox.information(
                    self,
                    "Information",
                    "Veuillez sélectionner une vente pour générer un ticket.",
                )
                return

        if self.selected_sale_id_for_details is not None:  # If a sale ID is available.
            try:
                # Generate the text content for the receipt.
                receipt_text = self.generate_receipt_text(
                    self.selected_sale_id_for_details
                )
                if receipt_text:  # If receipt text was generated successfully.
                    # Create and show the ReceiptDialog.
                    dialog = ReceiptDialog(
                        self.selected_sale_id_for_details,
                        receipt_text,
                        self,  # Pass ID, text, and parent.
                    )
                    dialog.exec()  # Show dialog modally.
                else:  # If receipt text generation failed.
                    QMessageBox.warning(
                        self,
                        "Erreur Ticket",
                        "Impossible de générer les données du ticket.",
                    )
            except (
                Exception
            ) as e:  # Handle errors during receipt generation or dialog display.
                QMessageBox.critical(
                    self,
                    "Erreur Ticket",
                    f"Erreur lors de la génération du ticket: {e}",
                )

    def generate_receipt_text(self, sale_id):
        """
        Constructs a formatted string representing a sales receipt for a given sale_id.
        Fetches sale header (date, customer, total) and sale items from the database.
        Args:
            sale_id (int): The ID of the sale for which to generate the receipt.
        Returns:
            str: A formatted receipt string, or None if data cannot be fetched.
        """
        try:
            conn = get_db_connection()  # Get database connection.
            cursor = conn.cursor()
            # Fetch main sale information (header).
            cursor.execute(
                "SELECT sale_date, customer_id, total_amount FROM Sales WHERE id = ?",
                (sale_id,),
            )
            sale_header = cursor.fetchone()  # Fetch one row.
            if not sale_header:  # If sale not found.
                conn.close()
                return None

            # Fetch customer details if customer_id is present.
            customer_info_str = "Client: Anonyme"  # Default for anonymous sales.
            if sale_header["customer_id"]:
                cursor.execute(
                    "SELECT name, address, phone FROM Customers WHERE id = ?",
                    (sale_header["customer_id"],),
                )
                cust = cursor.fetchone()
                if cust:  # If customer found, format their information.
                    customer_info_str = f"Client: {cust['name']}"
                    if cust["address"]:
                        customer_info_str += f"\nAdresse: {cust['address']}"
                    if cust["phone"]:
                        customer_info_str += f"\nTél: {cust['phone']}"
            conn.close()  # Close connection before calling another DB function that opens its own.

            items = get_sale_items(sale_id)  # Fetch all items for this sale.
            if (
                not items
            ):  # If no items found for the sale (should not happen for valid sales).
                return None

            # Start constructing the receipt string.
            receipt = f"--- TICKET DE VENTE ---\n\n"
            receipt += f"Vente ID: {sale_id}\n"
            try:  # Format date.
                dt_obj = datetime.datetime.fromisoformat(sale_header["sale_date"])
                receipt += f"Date: {dt_obj.strftime('%d/%m/%Y %H:%M:%S')}\n"
            except ValueError:  # Fallback if date format is unexpected.
                receipt += f"Date: {sale_header['sale_date']}\n"
            receipt += f"{customer_info_str}\n"  # Add customer info.
            receipt += f"{'-'*40}\n"  # Separator line.
            receipt += f"{'Produit':<20} {'Qté':>3} {'Prix U.':>8} {'Total':>8}\n"  # Item table header.
            receipt += f"{'-'*40}\n"

            # Add each item to the receipt.
            for item in items:
                # Truncate long product names for display.
                name = (
                    (item["product_name"][:18] + "..")  # Max 18 chars + "..".
                    if len(item["product_name"]) > 20
                    else item["product_name"]
                )
                qty, price, subtotal_val = (  # Format quantity, price, subtotal.
                    str(item["quantity"]),
                    f"{item['price_at_sale']:.2f}",
                    f"{item['quantity'] * item['price_at_sale']:.2f}",
                )
                # Add formatted item line to receipt. Left-align name, right-align others.
                receipt += f"{name:<20} {qty:>3} {price:>8} {subtotal_val:>8}\n"

            receipt += f"{'='*40}\n"  # Ending separator.
            # Add total amount, right-aligned.
            receipt += f"{'MONTANT TOTAL:':>32} {sale_header['total_amount']:.2f} DZD\n"
            receipt += f"\n--- Merci de votre achat ! ---\n"  # Closing message.
            return receipt
        except Exception as e:  # Handle any errors during receipt generation.
            print(f"Error generating receipt text for sale {sale_id}: {e}")
            QMessageBox.critical(
                self, "Erreur Interne", f"Une erreur interne est survenue: {str(e)}"
            )
            return None


class SaleDetailsDialog(QDialog):  # Dialog to display items of a specific sale.
    """
    A dialog window that shows the detailed list of products included in a specific sale.
    It takes the sale ID and a list of item data as input.
    """

    def __init__(self, sale_id, items_data, parent=None):  # Constructor.
        """
        Initializes the SaleDetailsDialog.
        Args:
            sale_id (int): The ID of the sale whose details are being displayed.
            items_data (list of dict): A list of dictionaries, each representing a sale item
                                       (e.g., {'product_name': ..., 'quantity': ..., 'price_at_sale': ...}).
            parent (QWidget, optional): The parent widget of this dialog.
        """
        super().__init__(parent)  # Call QDialog constructor.
        self.setWindowTitle(f"Détails de la Vente ID: {sale_id}")  # Set dialog title.
        self.setMinimumWidth(600)  # Set minimum width for better readability.
        self.setMinimumHeight(350)  # Set minimum height.
        self.sale_id = sale_id  # Store sale ID.

        # Style the dialog background and text color using theme.
        self.setStyleSheet(
            f"background-color: {COLORS.get('surface', '#ffffff')}; color: {COLORS.get('text_primary', '#000000')};"
        )

        layout = QVBoxLayout(self)  # Main vertical layout for the dialog.
        # Set margins and spacing using theme values.
        layout.setContentsMargins(
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
        )
        layout.setSpacing(int(SPACING["md"].replace("px", "")))

        # Table to display sale items.
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(
            4
        )  # Four columns: Product, Quantity, Unit Price, Subtotal.
        self.details_table.setHorizontalHeaderLabels(
            ["Produit", "Quantité", "Prix Unit.", "Sous-Total"]
        )
        self.details_table.setStyleSheet(
            STYLES.get("table", "")
        )  # Apply themed table style.
        self.details_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # Read-only table.
        self.details_table.verticalHeader().setVisible(False)  # Hide row numbers.
        # Stretch columns to fill width.
        self.details_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.details_table)  # Add table to layout.
        self.populate_table(items_data)  # Populate the table with provided item data.

        # "OK" button to close the dialog.
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(
            self.accept
        )  # Standard accept action (closes dialog).
        self.ok_button.setStyleSheet(STYLES.get("button_primary", ""))  # Themed button.
        self.ok_button.setMinimumHeight(35)
        self.ok_button.setMinimumWidth(100)

        # Layout for the OK button (centered).
        button_box_layout = QHBoxLayout()
        button_box_layout.addStretch()  # Push button to center.
        button_box_layout.addWidget(self.ok_button)
        button_box_layout.addStretch()  # Push button to center.
        layout.addLayout(button_box_layout)

        self.setLayout(layout)  # Apply the main layout to the dialog.

    def populate_table(self, items_data):
        """
        Populates the details_table with the provided sale item data.
        Args:
            items_data (list of dict): List of sale items.
        """
        self.details_table.setRowCount(0)  # Clear existing rows.
        if items_data:  # If there are items to display.
            self.details_table.setRowCount(len(items_data))  # Set row count.
            for row_idx, item in enumerate(items_data):
                # Calculate subtotal for the item.
                subtotal = item["quantity"] * item["price_at_sale"]
                # Populate cells.
                self.details_table.setItem(
                    row_idx, 0, QTableWidgetItem(item["product_name"])  # Product name.
                )
                self.details_table.setItem(
                    row_idx, 1, QTableWidgetItem(str(item["quantity"]))  # Quantity.
                )
                self.details_table.setItem(
                    row_idx,
                    2,
                    QTableWidgetItem(f"{item['price_at_sale']:.2f} DZD"),  # Unit price.
                )
                self.details_table.setItem(
                    row_idx, 3, QTableWidgetItem(f"{subtotal:.2f} DZD")  # Subtotal.
                )


class ReceiptDialog(QDialog):  # Dialog to display a formatted sales receipt.
    """
    A dialog window that displays a plain text sales receipt.
    The receipt text is pre-formatted and passed to this dialog.
    """

    def __init__(self, sale_id, receipt_text, parent=None):  # Constructor.
        """
        Initializes the ReceiptDialog.
        Args:
            sale_id (int): The ID of the sale for which the receipt is displayed.
            receipt_text (str): The pre-formatted string content of the receipt.
            parent (QWidget, optional): The parent widget of this dialog.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Ticket de Vente - ID: {sale_id}")  # Set dialog title.
        self.setMinimumSize(480, 550)  # Set minimum size for the dialog.

        # Style the dialog background using theme.
        self.setStyleSheet(f"background-color: {COLORS.get('surface', '#ffffff')};")

        layout = QVBoxLayout(self)  # Main vertical layout.
        # Set margins and spacing using theme.
        layout.setContentsMargins(
            int(SPACING["md"].replace("px", "")),
            int(SPACING["md"].replace("px", "")),
            int(SPACING["md"].replace("px", "")),
            int(SPACING["md"].replace("px", "")),
        )
        layout.setSpacing(int(SPACING["sm"].replace("px", "")))

        # QTextEdit to display the receipt text (read-only).
        self.receipt_display = QTextEdit()
        self.receipt_display.setReadOnly(True)  # Make it non-editable.
        # Use a monospaced font for receipt display, for better alignment of text.
        self.receipt_display.setFont(
            QFont(FONTS.get("family_mono", "Courier New"), FONTS.get("sm", 10))
        )
        self.receipt_display.setText(receipt_text)  # Set the receipt content.
        # Apply styling to the QTextEdit (e.g., background, border, padding).
        self.receipt_display.setStyleSheet(
            STYLES.get(
                "text_area_receipt",  # Attempt to get a specific style from theme.
                # Fallback style if "text_area_receipt" is not in STYLES:
                f"""
            QTextEdit {{
                background-color: {COLORS.get('gray_50', '#f8fafc')}; /* Light gray background. */
                color: {COLORS.get('text_primary', '#0f172a')}; /* Standard text color. */
                border: 1px solid {COLORS.get('border', '#e2e8f0')}; /* Border. */
                padding: {SPACING.get('md', '12px')}; /* Padding. */
                border-radius: {RADIUS.get('sm','6px')}; /* Rounded corners. */
            }}
            """,
            )
        )
        layout.addWidget(self.receipt_display)  # Add text area to layout.

        # "Close" button to dismiss the dialog.
        self.close_button = QPushButton("Fermer")
        self.close_button.clicked.connect(
            self.reject
        )  # Standard reject action (closes dialog).
        self.close_button.setStyleSheet(
            STYLES.get("button_primary", "")
        )  # Themed button.
        self.close_button.setMinimumHeight(35)
        self.close_button.setMinimumWidth(100)

        # Layout for the close button (centered).
        button_box_layout = QHBoxLayout()
        button_box_layout.addStretch()
        button_box_layout.addWidget(self.close_button)
        button_box_layout.addStretch()
        layout.addLayout(button_box_layout)

        self.setLayout(layout)  # Apply main layout to dialog.


if (
    __name__ == "__main__"
):  # This block runs if the script is executed directly (for testing).
    # Import necessary functions for setting up a test environment.
    from database.database import initialize_database, add_product, add_customer
    from PyQt6.QtWidgets import QApplication
    from theme import apply_global_style  # Function to apply global application theme.

    initialize_database()  # Ensure database and tables exist.
    # Add some sample data if database is empty, for testing purposes.
    if not get_all_products():  # Check if there are any products.
        add_product("Produit Test Sale A", "Desc A", "Cat Test S", 5.0, 10.0, 20)
        add_product("Produit Test Sale B", "Desc B", "Cat Test S", 12.5, 25.0, 15)
    if not get_all_customers():  # Check if there are any customers.
        add_customer(
            "Client Essai Sale", "123 Rue Test", "0102030405", "sale@example.com"
        )

    app = QApplication(sys.argv)  # Create the QApplication instance.
    apply_global_style(app)  # Apply the global theme to the application.
    sale_widget = SaleView()  # Create an instance of the SaleView.
    sale_widget.show()  # Display the SaleView widget.
    sys.exit(app.exec())  # Start the Qt application event loop.
