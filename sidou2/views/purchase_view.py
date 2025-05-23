# Updated content for sidou2/views/purchase_view.py
import sys  # Standard Python library for system-specific parameters and functions.
import datetime  # Standard Python library for working with dates and times.
from PyQt6.QtWidgets import (  # Import necessary UI components from PyQt6.
    QApplication,  # Manages the application's control flow and main settings.
    QWidget,  # Base class for all UI objects.
    QVBoxLayout,  # Arranges widgets vertically.
    QHBoxLayout,  # Arranges widgets horizontally.
    QLabel,  # Displays text or images.
    QPushButton,  # Represents a command button.
    QTableWidget,  # Provides a table display.
    QTableWidgetItem,  # Represents an item in a QTableWidget.
    QMessageBox,  # Displays modal dialogs for messages.
    QHeaderView,  # Provides header rows or columns for item views.
    QAbstractItemView,  # Provides an abstract model for item views.
    QComboBox,  # Provides a dropdown list of items.
    QSpinBox,  # Allows integer input via up/down arrows or direct typing.
    QDoubleSpinBox,  # Allows floating-point input via up/down arrows or direct typing.
    QLineEdit,  # Allows single-line text input.
    QGridLayout,  # Arranges widgets in a grid layout.
    QSpacerItem,  # Represents a blank space in a layout.
    QSizePolicy,  # Describes how a widget should resize.
    QFrame,  # Provides a frame, often used as a container or for styling.
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)  # Import core Qt functionalities like alignment flags and signals.

# Import custom theme settings (colors, fonts, spacing, radius, styles).
from theme import COLORS, FONTS, SPACING, RADIUS, STYLES

# Import database interaction functions.
from database.database import (
    add_purchase,  # Function to add a new purchase record.
    get_purchase_history,  # Function to retrieve purchase history.
    get_all_products,  # Function to retrieve all products (for product selection).
    add_product,  # Function to add a new product (example usage in __main__).
    get_product_by_id,  # Function to retrieve a product by its ID.
)
from .base_view import BaseView  # Import BaseView for common UI functionalities.
from utils.error_handler import DatabaseError  # Import custom DatabaseError exception.


class PurchaseView(BaseView):  # PurchaseView class inherits from BaseView.
    # Define a signal that is emitted when a new purchase is successfully recorded.
    # This can be used to notify other parts of the application (e.g., to refresh stock levels).
    purchase_recorded = pyqtSignal()

    def __init__(self):
        """
        Constructor for the PurchaseView.
        Initializes the UI for recording new purchases and viewing purchase history.
        """
        super().__init__(
            "Enregistrer un Achat Fournisseur"  # Call BaseView's constructor with the window title.
        )
        self.products_data = (
            {}
        )  # Cache to store product data (e.g., for the product dropdown).
        self._init_ui_elements()  # Initialize UI elements specific to this view.
        self.load_products_for_combo()  # Load products into the product selection dropdown.
        self.load_purchase_history()  # Load and display existing purchase history.

    def _init_ui_elements(self):
        """
        Initializes the user interface elements of the PurchaseView.
        Sets up the form for adding new purchases and the table for displaying purchase history.
        """
        self.create_title()  # Use BaseView's method to create and display the view title.

        # --- Form Section for Adding a New Purchase ---
        # Create a QFrame to act as a styled card for the purchase form.
        form_card = QFrame()
        form_card.setStyleSheet(
            STYLES.get("card", "")
        )  # Apply card style from the theme.
        # Create a vertical layout for the content within the form card.
        form_layout_outer = QVBoxLayout(form_card)
        # Set content margins for the form card using spacing values from the theme.
        form_layout_outer.setContentsMargins(
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
        )

        # Create a grid layout for arranging form elements (labels and input fields).
        form_grid_layout = QGridLayout()
        form_grid_layout.setSpacing(
            int(SPACING["md"].replace("px", ""))
        )  # Set spacing between grid cells.

        # --- Form Row 1: Product Selection and Quantity Input ---
        product_label = QLabel(
            "Produit*:"
        )  # Label for product selection (asterisk indicates required).
        self.product_combo = QComboBox()  # Dropdown for selecting a product.
        quantity_label = QLabel("Quantité*:")  # Label for quantity input.
        self.quantity_spinbox = QSpinBox()  # Spinbox for entering purchase quantity.
        self.quantity_spinbox.setRange(1, 99999)  # Set min and max allowed quantity.

        # Add product and quantity widgets to the grid layout.
        form_grid_layout.addWidget(product_label, 0, 0)  # Row 0, Col 0.
        form_grid_layout.addWidget(self.product_combo, 0, 1)  # Row 0, Col 1.
        form_grid_layout.addWidget(quantity_label, 0, 2)  # Row 0, Col 2.
        form_grid_layout.addWidget(self.quantity_spinbox, 0, 3)  # Row 0, Col 3.

        # --- Form Row 2: Cost Per Unit and Supplier Input ---
        cost_label = QLabel("Coût Unitaire*:")  # Label for cost per unit.
        self.cost_spinbox = (
            QDoubleSpinBox()
        )  # Spinbox for entering cost (allows decimals).
        self.cost_spinbox.setRange(0.0, 999999.99)  # Set min and max allowed cost.
        self.cost_spinbox.setDecimals(2)  # Allow two decimal places for currency.
        self.cost_spinbox.setSuffix(" DZD")  # Display currency suffix.
        supplier_label = QLabel("Fournisseur:")  # Label for supplier name (optional).
        self.supplier_input = QLineEdit()  # Text input for supplier name.
        self.supplier_input.setPlaceholderText("(Optionnel)")  # Placeholder text.

        # Add cost and supplier widgets to the grid layout.
        form_grid_layout.addWidget(cost_label, 1, 0)  # Row 1, Col 0.
        form_grid_layout.addWidget(self.cost_spinbox, 1, 1)  # Row 1, Col 1.
        form_grid_layout.addWidget(supplier_label, 1, 2)  # Row 1, Col 2.
        form_grid_layout.addWidget(self.supplier_input, 1, 3)  # Row 1, Col 3.

        # Apply common styles to form labels and input widgets using BaseView methods.
        self.apply_label_styles(
            [product_label, quantity_label, cost_label, supplier_label]
        )
        self.apply_input_styles(
            [
                self.product_combo,
                self.quantity_spinbox,
                self.cost_spinbox,
                self.supplier_input,
            ]
        )

        # --- Form Row 3: Add Purchase Button ---
        # Create the "Enregistrer l'Achat" (Record Purchase) button using BaseView's method.
        self.add_purchase_button = self.create_button(
            "Enregistrer l'Achat",
            self.add_new_purchase,
            style_key="button_primary",  # Text, callback, style.
        )
        # Add button to the grid layout, spanning all 4 columns.
        form_grid_layout.addWidget(
            self.add_purchase_button, 2, 0, 1, 4
        )  # Row 2, Col 0, spans 1 row, 4 columns.

        form_layout_outer.addLayout(
            form_grid_layout
        )  # Add the grid layout to the form card's main layout.
        self.main_layout.addWidget(
            form_card
        )  # Add the form card to the view's main layout.

        # --- Purchase History Section ---
        # Create a title label for the purchase history section.
        history_title_label = QLabel("Historique des Achats Récents")
        # Apply subtitle style from the theme, with fallbacks.
        history_title_label.setStyleSheet(
            STYLES.get(
                "subtitle",
                f"font-size: {FONTS['subtitle']}pt; font-weight: bold; "
                f"margin-top: {SPACING['xl']}; margin-bottom: {SPACING['sm']};"
                f"color: {COLORS['text_secondary']};",
            )
        )
        self.main_layout.addWidget(
            history_title_label
        )  # Add history title to the main layout.

        # Create the table to display purchase history using BaseView's helper method.
        self.history_table = self.create_table(
            [
                "ID Achat",
                "Date",
                "Produit",
                "Quantité",
                "Coût Unit.",
                "Fournisseur",
            ],  # Define column headers.
            selection_mode="none",  # Disable row selection in the history table.
        )
        # Configure how columns resize.
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch  # Stretch most columns to fill available width.
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,  # Resize ID Achat column to fit content.
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,  # Resize Date column to fit content.
        )
        self.main_layout.addWidget(
            self.history_table
        )  # Add history table to the main layout.

        # Create a horizontal layout for buttons at the bottom of the history section.
        button_layout_bottom = self.create_button_layout()  # Use BaseView's method.
        # Create the "Rafraîchir l'Historique" (Refresh History) button.
        self.refresh_button = self.create_button(
            "Rafraîchir l'Historique",
            self.load_purchase_history,  # Callback to reload history data.
            style_key="button_secondary",  # Apply secondary button style.
        )

        button_layout_bottom.addStretch()  # Add stretch to push refresh button to the right.
        button_layout_bottom.addWidget(self.refresh_button)
        self.main_layout.addLayout(
            button_layout_bottom
        )  # Add button layout to the main view layout.

        self.main_layout.addStretch(
            1
        )  # Add stretch at the end of the main_layout to push content upwards.

    def load_products_for_combo(self):
        """
        Loads product data from the database and populates the product selection dropdown (QComboBox).
        Stores product IDs in the `products_data` cache for later retrieval.
        """
        self.product_combo.clear()  # Clear existing items from the dropdown.
        self.products_data.clear()  # Clear the product data cache.
        self.product_combo.addItem(
            "Sélectionner un produit...", -1
        )  # Add a default placeholder item.
        # -1 can be used as user data for the placeholder.
        try:
            products = get_all_products()  # Fetch all products from the database.
            if products:
                for product in products:
                    # Create a display text showing product name and current stock.
                    display_text = (
                        f"{product['name']} (Stock: {product['quantity_in_stock']})"
                    )
                    # Add item to dropdown: display text and product ID as item data.
                    self.product_combo.addItem(display_text, product["id"])
                    # Store product ID in cache, keyed by display text (alternative: key by ID if preferred).
                    self.products_data[display_text] = product["id"]
        except DatabaseError as e:  # Catch specific database errors.
            self.show_error(
                "Erreur Produits", f"Impossible de charger la liste des produits: {e}"
            )
        except Exception as e:  # Catch any other unexpected errors.
            self.show_error(
                "Erreur Inattendue",
                f"Une erreur s'est produite lors du chargement des produits: {e}",
            )

    def load_purchase_history(self):
        """
        Loads purchase history from the database and populates the history table.
        Formats dates and currency for display.
        """
        self.history_table.setRowCount(0)  # Clear existing rows from the table.
        try:
            history = (
                get_purchase_history()
            )  # Fetch purchase history (typically recent records).
            if history:
                self.history_table.setRowCount(
                    len(history)
                )  # Set table rows based on number of history records.
                for row_idx, purchase in enumerate(
                    history
                ):  # Iterate through history records.
                    # Create QTableWidgetItem for each piece of purchase data.
                    self.history_table.setItem(
                        row_idx,
                        0,
                        QTableWidgetItem(str(purchase["id"])),  # Purchase ID.
                    )
                    date_str = purchase["purchase_date"]  # Get purchase date string.
                    try:
                        # Attempt to parse ISO date string and format it for display.
                        dt_obj = datetime.datetime.fromisoformat(date_str)
                        display_date = dt_obj.strftime(
                            "%Y-%m-%d %H:%M"
                        )  # Format as YYYY-MM-DD HH:MM.
                    except ValueError:
                        display_date = (
                            date_str  # Fallback to original string if parsing fails.
                        )
                    self.history_table.setItem(
                        row_idx,
                        1,
                        QTableWidgetItem(display_date),  # Formatted purchase date.
                    )
                    self.history_table.setItem(
                        row_idx,
                        2,
                        QTableWidgetItem(purchase["product_name"]),  # Product name.
                    )
                    self.history_table.setItem(
                        row_idx,
                        3,
                        QTableWidgetItem(
                            str(purchase["quantity"])
                        ),  # Quantity purchased.
                    )
                    self.history_table.setItem(
                        row_idx,
                        4,
                        QTableWidgetItem(
                            f"{purchase['cost_per_unit']:.2f} DZD"
                        ),  # Cost per unit, formatted as currency.
                    )
                    self.history_table.setItem(
                        row_idx,
                        5,
                        QTableWidgetItem(
                            purchase["supplier"] or ""
                        ),  # Supplier name, or empty string if None.
                    )
        except DatabaseError as e:  # Catch specific database errors.
            self.show_error(
                "Erreur Historique",
                f"Impossible de charger l'historique des achats: {e}",
            )
        except Exception as e:  # Catch any other unexpected errors.
            self.show_error(
                "Erreur Inattendue",
                f"Une erreur s'est produite lors du chargement de l'historique: {e}",
            )

    def add_new_purchase(self):
        """
        Handles the recording of a new purchase.
        Retrieves data from form fields, validates it, calls the database function to add the purchase,
        and then refreshes relevant UI parts (history, product list for stock updates).
        """
        selected_index = (
            self.product_combo.currentIndex()
        )  # Get index of selected product in dropdown.
        # Validate that a product is selected (index > 0 because 0 is the placeholder).
        if selected_index <= 0:
            self.show_warning(
                "Attention", "Veuillez sélectionner un produit."
            )  # Show warning if no product selected.
            return

        product_id = self.product_combo.itemData(
            selected_index
        )  # Get product ID stored as item data.
        quantity = self.quantity_spinbox.value()  # Get quantity from spinbox.
        cost = self.cost_spinbox.value()  # Get cost from double spinbox.
        supplier = (
            self.supplier_input.text().strip() or None
        )  # Get supplier name, or None if empty.

        # Validate quantity and cost.
        if quantity <= 0 or cost < 0:
            self.show_warning(
                "Attention",
                "La quantité doit être positive et le coût doit être positif ou nul.",
            )
            return
        try:  # Wrap database operation in a try-except block.
            new_purchase_id = add_purchase(
                product_id, quantity, cost, supplier
            )  # Call DB function.
            if new_purchase_id:  # If purchase was successfully added (returns ID).
                self.show_info(
                    "Succès",
                    f"Achat pour le produit ID {product_id} enregistré.",  # Show success message.
                )
                self.load_purchase_history()  # Refresh the purchase history table.
                self.load_products_for_combo()  # Reload products (stock levels will have changed).
                # Clear form fields for the next entry.
                self.product_combo.setCurrentIndex(
                    0
                )  # Reset product dropdown to placeholder.
                self.quantity_spinbox.setValue(1)  # Reset quantity to 1.
                self.cost_spinbox.setValue(0.0)  # Reset cost to 0.0.
                self.supplier_input.clear()  # Clear supplier input.
                self.purchase_recorded.emit()  # Emit signal indicating a purchase was made.
            else:  # Should not happen if add_purchase raises an error or returns an ID.
                self.show_error(
                    "Erreur", "L'achat n'a pas pu être enregistré."
                )  # Generic error if no ID returned.
        except DatabaseError as e:  # Catch specific database errors.
            self.show_error(
                "Erreur Base de Données",
                f"Erreur lors de l'enregistrement de l'achat: {e}",
            )
        except Exception as e:  # Catch any other unexpected errors.
            self.show_error(
                "Erreur Inattendue", f"Une erreur inattendue est survenue: {e}"
            )


# This block allows the PurchaseView to be run standalone for testing purposes.
if __name__ == "__main__":
    from database.database import (
        initialize_database,
    )  # For setting up DB if run standalone.
    from theme import apply_global_style  # For applying the application theme.

    initialize_database()  # Ensure database and tables exist.
    # Add a sample product if none exist, to test the product dropdown.
    if not get_all_products():
        add_product("Produit Test Purchase", "Desc", "Cat Test P", 10.0, 20.0, 5)

    app = QApplication(sys.argv)  # Create the PyQt application instance.
    apply_global_style(app)  # Apply the global theme to the application.
    purchase_widget = PurchaseView()  # Create an instance of PurchaseView.
    purchase_widget.show()  # Display the PurchaseView widget.
    sys.exit(app.exec())  # Start the Qt application event loop.
