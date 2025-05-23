# Updated content for sidou2/views/product_view.py
# Import necessary modules from PyQt6 for creating the GUI
from PyQt6.QtWidgets import (
    QWidget,  # Base class for all UI objects
    QVBoxLayout,  # Arranges widgets vertically
    QHBoxLayout,  # Arranges widgets horizontally
    QLabel,  # Displays text or images
    QLineEdit,  # Single-line text input
    QPushButton,  # Command button
    QTextEdit,  # Multi-line rich text editor
    QTableWidget,  # Displays data in a table
    QTableWidgetItem,  # Represents an item in a QTableWidget
    QMessageBox,  # Standard dialog box for messages
    QHeaderView,  # Provides header rows or columns for item views
    QAbstractItemView,  # Abstract base class for item views
    QDoubleSpinBox,  # Spin box for floating-point numbers
    QComboBox,  # Drop-down list box
    QGridLayout,  # Arranges widgets in a grid
    QMenu,  # Provides a context menu or pull-down menu
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)  # Core Qt functionalities, including signals and alignment flags
from PyQt6.QtGui import (
    QAction,
)  # Represents an action that can be triggered by a menu or toolbar

# Import custom modules from the project
from views.base_view import (
    BaseView,
)  # Base class for all views, providing common functionality
from utils.error_handler import (
    DatabaseError,
    ValidationError,
)  # Custom error classes for database and validation issues
from theme import (
    STYLES,
    COLORS,
    FONTS,
    SPACING,
    RADIUS,
)  # Theme settings (styles, colors, fonts, etc.)
from database.database import (  # Functions for interacting with the database
    get_all_products,  # Retrieves all products from the database
    add_product,  # Adds a new product to the database
    update_product,  # Updates an existing product in the database
    delete_product,  # Deletes a product from the database
    search_products,  # Searches for products based on criteria
    get_all_categories,  # Retrieves all unique product categories
)


class ProductView(BaseView):  # ProductView class, inherits from BaseView
    """
    Manages the UI for product management.
    This includes displaying products, adding new products,
    updating existing ones, and deleting products.
    It inherits common UI functionalities from BaseView.
    """

    # Signal emitted when a product is added, updated, or deleted,
    # allowing other parts of the application to refresh their data.
    product_updated = pyqtSignal()

    def __init__(self):
        """
        Constructor for ProductView.
        Initializes the UI elements, loads categories for filtering,
        and loads the initial list of products.
        """
        super().__init__(
            "Gestion des Produits"
        )  # Call BaseView constructor, passing the view title
        self.current_product_id = None  # Stores the ID of the currently selected product in the table (None if no selection)
        self.visible_columns = list(
            range(7)
        )  # List of column indices that are currently visible in the product table
        # Default: ID, Nom, Cat, Desc, PA, PV, Stock

        self.init_ui_product()  # Initialize the specific UI elements for the product view
        self.load_categories()  # Load product categories into the filter combo box
        self.load_products()  # Load and display the list of products in the table

    def init_ui_product(self):
        """
        Initializes the user interface elements specific to the ProductView.
        This includes search/filter inputs, a form for product details,
        CRUD buttons, and the product table.
        The main title is created by the BaseView's __init__ method.
        """

        # Create search input and category filter combo box using a BaseView helper method
        # These allow users to filter the product list.
        self.search_input, self.category_filter_combo = (
            self.create_search_filter_layout(
                search_placeholder="Rechercher par nom/description...",  # Placeholder text for the search input
                with_category_filter=True,  # Indicates that a category filter should be included
            )
        )
        # Connect signals from search and filter widgets to the filter_products method
        if self.search_input:  # Check if search_input was successfully created
            self.search_input.textChanged.connect(
                self.filter_products
            )  # Trigger filter on text change
        if (
            self.category_filter_combo
        ):  # Check if category_filter_combo was successfully created
            self.category_filter_combo.currentIndexChanged.connect(
                self.filter_products
            )  # Trigger filter on selection change

        # Create a styled widget and layout for the product input form using a BaseView helper method
        form_widget, form_layout = self.create_form_widget()

        # --- Form Fields ---
        # Labels and input fields for product details (name, category, description, prices)
        name_label = QLabel(
            "Nom*:"
        )  # Label for product name (asterisk indicates required field)
        self.name_input = QLineEdit()  # Input field for product name

        category_label_form = QLabel("Catégorie*:")  # Label for product category
        self.category_input = QLineEdit()  # Input field for product category
        self.category_input.setPlaceholderText(
            "Nouvelle ou existante"
        )  # Placeholder text for category input

        description_label = QLabel("Description:")  # Label for product description
        self.description_input = (
            QTextEdit()
        )  # Text area for longer product descriptions
        # self.description_input.setFixedHeight(70) # Height can be part of theme.STYLES['input'] or handled by apply_input_styles

        purchase_price_label = QLabel("Prix d'achat*:")  # Label for purchase price
        self.purchase_price_input = (
            QDoubleSpinBox()
        )  # Spin box for purchase price (allows decimals)
        self.purchase_price_input.setRange(0.0, 999999.99)  # Set allowed price range
        self.purchase_price_input.setDecimals(2)  # Set number of decimal places
        self.purchase_price_input.setSuffix(" DZD")  # Add currency suffix

        selling_price_label = QLabel("Prix de vente*:")  # Label for selling price
        self.selling_price_input = QDoubleSpinBox()  # Spin box for selling price
        self.selling_price_input.setRange(0.0, 999999.99)  # Set allowed price range
        self.selling_price_input.setDecimals(2)  # Set number of decimal places
        self.selling_price_input.setSuffix(" DZD")  # Add currency suffix

        # Apply common styling to all input fields using a BaseView helper method
        self.apply_input_styles(
            [
                self.name_input,
                self.category_input,
                self.description_input,
                self.purchase_price_input,
                self.selling_price_input,
            ]
        )
        # Apply styling to labels in the form, making them bold
        self.apply_label_styles(
            [
                name_label,
                category_label_form,
                description_label,
                purchase_price_label,
                selling_price_label,
            ],
            style_key="label_bold",  # Use the 'label_bold' style from the theme
        )

        # Add labels and input fields to the form_layout (a QGridLayout)
        # Arguments for addWidget: widget, row, column, rowSpan (optional), columnSpan (optional)
        form_layout.addWidget(name_label, 0, 0)  # Row 0, Col 0
        form_layout.addWidget(self.name_input, 0, 1)  # Row 0, Col 1
        form_layout.addWidget(category_label_form, 0, 2)  # Row 0, Col 2
        form_layout.addWidget(self.category_input, 0, 3)  # Row 0, Col 3
        form_layout.addWidget(description_label, 1, 0)  # Row 1, Col 0
        form_layout.addWidget(
            self.description_input, 1, 1, 1, 3
        )  # Row 1, Col 1, spans 1 row, 3 columns
        form_layout.addWidget(purchase_price_label, 2, 0)  # Row 2, Col 0
        form_layout.addWidget(self.purchase_price_input, 2, 1)  # Row 2, Col 1
        form_layout.addWidget(selling_price_label, 2, 2)  # Row 2, Col 2
        form_layout.addWidget(self.selling_price_input, 2, 3)  # Row 2, Col 3

        # Add the entire form widget (containing the grid layout) to the main view layout
        self.main_layout.addWidget(form_widget)

        # --- CRUD Buttons ---
        # Create Add, Update, Delete, and Clear buttons using a BaseView helper method
        # This method also connects them to their respective handler functions.
        self.add_button, self.update_button, self.delete_button, self.clear_button = (
            self.create_crud_buttons(
                add_handler=self.add_new_product,  # Function to call when 'Add' is clicked
                update_handler=self.update_selected_product,  # Function for 'Update'
                delete_handler=self.delete_selected_product,  # Function for 'Delete'
                clear_handler=self.clear_form,  # Function for 'Clear'
            )
        )
        # Set tooltips for the CRUD buttons to provide users with hints
        if self.add_button:
            self.add_button.setToolTip(
                "Ajouter un nouveau produit avec les informations saisies"
            )
        if self.update_button:
            self.update_button.setToolTip(
                "Mettre à jour le produit sélectionné avec les nouvelles informations"
            )
        if self.delete_button:
            self.delete_button.setToolTip(
                "Supprimer définitivement le produit sélectionné"
            )
        if self.clear_button:
            self.clear_button.setToolTip(
                "Effacer toutes les informations saisies dans le formulaire"
            )

        # --- Product Table ---
        # Create the table to display products using a BaseView helper method
        self.product_table = self.create_table(
            columns=[  # Define the column headers for the table
                "ID",
                "Nom",
                "Catégorie",
                "Description",
                "Prix Achat",
                "Prix Vente",
                "Stock",
            ]
        )
        # Configure column resizing behavior
        self.product_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,  # Resize 'ID' column to fit content
        )
        self.product_table.horizontalHeader().setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.ResizeToContents,  # Resize 'Stock' column to fit content
        )
        # By default, hide the 'Description' column as it can be lengthy
        self.product_table.setColumnHidden(3, True)
        if (
            3 in self.visible_columns
        ):  # If 'Description' (index 3) was in visible_columns, remove it
            self.visible_columns.remove(3)

        # Connect signals from the table
        self.product_table.itemSelectionChanged.connect(
            self.on_row_selected
        )  # Trigger when table selection changes
        # Enable custom context menu for the table header (to show/hide columns)
        self.product_table.horizontalHeader().setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.product_table.horizontalHeader().customContextMenuRequested.connect(
            self.show_column_menu
        )
        # Add the product table to the main view layout
        self.main_layout.addWidget(self.product_table)
        # self.setLayout(self.main_layout) # This is handled by BaseView constructor

    def load_categories(self):
        """
        Loads product categories from the database and populates the category filter combo box.
        Uses a BaseView helper method for populating the combo box.
        """
        if not self.category_filter_combo:  # If the combo box doesn't exist, do nothing
            return
        # Call the BaseView helper to populate the combo box
        self.populate_category_combo(self.category_filter_combo)

    def add_new_product(self):
        """
        Handles adding a new product.
        Retrieves data from the input fields, validates it,
        calls the database function to add the product,
        and then refreshes the UI.
        """
        # Get product details from input fields, stripping leading/trailing whitespace
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()  # For QTextEdit
        category = self.category_input.text().strip()
        purchase_price = self.purchase_price_input.value()  # For QDoubleSpinBox
        selling_price = self.selling_price_input.value()

        try:
            # Basic validation for required fields
            if not name:
                self.show_warning(
                    "Champ Requis", "Le nom du produit est obligatoire."
                )  # Show warning if name is empty
                return
            if not category:
                self.show_warning(
                    "Champ Requis",
                    "La catégorie du produit est obligatoire.",  # Show warning if category is empty
                )
                return

            # Call the database function to add the product
            product_id = add_product(
                name, description, category, purchase_price, selling_price
            )
            # After successful addition:
            self.clear_form()  # Clear the input fields
            self.load_products()  # Reload the product list in the table
            self.load_categories()  # Reload categories (in case a new one was added)
            self.product_updated.emit()  # Emit signal that product data has changed
            self.show_info(
                "Succès", f"Le produit '{name}' a été ajouté."
            )  # Show success message
        except (
            ValidationError
        ) as ve:  # Handle validation errors (defined in error_handler.py)
            self.show_error("Erreur de Validation", str(ve))
        except (
            DatabaseError
        ) as de:  # Handle database errors (defined in error_handler.py)
            self.show_error("Erreur Base de Données", str(de))
        except Exception as e:  # Handle any other unexpected errors
            self.show_error("Erreur Inattendue", f"Une erreur est survenue: {str(e)}")

    def update_selected_product(self):
        """
        Handles updating the currently selected product.
        Retrieves data from input fields, validates it,
        calls the database function to update, and refreshes the UI.
        """
        if not self.current_product_id:  # Check if a product is selected
            self.show_warning(
                "Aucune Sélection", "Veuillez sélectionner un produit à modifier."
            )
            return

        # Get updated product details from input fields
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        description = self.description_input.toPlainText().strip()
        purchase_price = self.purchase_price_input.value()
        selling_price = self.selling_price_input.value()

        try:
            # Basic validation for required fields
            if not name:
                self.show_warning("Champ Requis", "Le nom du produit est obligatoire.")
                return
            if not category:
                self.show_warning(
                    "Champ Requis", "La catégorie du produit est obligatoire."
                )
                return

            # Call database function to update the product
            success = update_product(
                self.current_product_id,  # ID of the product to update
                name,
                description,
                category,
                purchase_price,
                selling_price,
            )
            if success:  # If update was successful
                self.load_products()  # Reload product list
                self.load_categories()  # Reload categories
                self.product_updated.emit()  # Emit signal
                self.show_info(
                    "Succès", "Le produit a été modifié."
                )  # Show success message
                self.clear_form()  # Clear the form
            else:  # If update_product returns False (e.g., product not found, though DB errors are caught)
                self.show_error("Échec", "La modification du produit a échoué.")
        except ValidationError as ve:
            self.show_error("Erreur de Validation", str(ve))
        except DatabaseError as de:
            self.show_error("Erreur Base de Données", str(de))
        except Exception as e:
            self.show_error(
                "Erreur Inattendue", f"Erreur lors de la modification: {str(e)}"
            )

    def delete_selected_product(self):
        """
        Handles deleting the currently selected product.
        Shows a confirmation dialog before calling the database function to delete.
        """
        if not self.current_product_id:  # Check if a product is selected
            self.show_warning(
                "Aucune Sélection", "Veuillez sélectionner un produit à supprimer."
            )
            return

        # Show a confirmation dialog before deleting
        if self.show_confirmation(
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce produit ?\nCette action est irréversible.",
        ):
            try:
                # Call database function to delete the product
                success = delete_product(self.current_product_id)
                if success:  # If deletion was successful
                    self.clear_form()  # Clear the form
                    self.load_products()  # Reload product list
                    self.load_categories()  # Reload categories
                    self.product_updated.emit()  # Emit signal
                    self.show_info(
                        "Succès", "Le produit a été supprimé."
                    )  # Show success message
                else:  # If delete_product returns False (e.g., product not found or deletion restricted by DB)
                    self.show_error(
                        "Échec",
                        "La suppression du produit a échoué. Il est peut-être utilisé dans des ventes.",
                    )
            except (
                DatabaseError
            ) as de:  # Handle specific DB errors (e.g., foreign key constraint)
                self.show_error("Erreur Suppression", str(de))
            except Exception as e:
                self.show_error(
                    "Erreur Inattendue", f"Erreur lors de la suppression: {str(e)}"
                )

    def load_products(self):
        """
        Loads products from the database based on current search and filter criteria,
        then populates the product table with this data.
        Manages column visibility based on self.visible_columns.
        """
        # Get current search query and category filter
        search_query = self.search_input.text().strip() if self.search_input else ""
        category = (
            self.category_filter_combo.currentText()
            if self.category_filter_combo  # Check if combo box exists
            and self.category_filter_combo.currentIndex()
            > 0  # Ensure an actual category is selected (not "Toutes...")
            else None
        )
        if (
            category == "Toutes les catégories"
        ):  # Treat "Toutes les catégories" as no filter
            category = None

        self.product_table.setRowCount(0)  # Clear existing rows in the table
        try:
            # Search for products in the database using the current filters
            products = search_products(search_query, category)
            self.product_table.setRowCount(
                len(products)
            )  # Set table rows to the number of products found

            # Populate the table row by row
            for row_idx, product in enumerate(products):
                # Create QTableWidgetItem for each piece of product data and add to the table
                self.product_table.setItem(
                    row_idx, 0, QTableWidgetItem(str(product["id"]))  # Product ID
                )
                self.product_table.setItem(
                    row_idx, 1, QTableWidgetItem(product["name"])  # Name
                )
                self.product_table.setItem(
                    row_idx,
                    2,
                    QTableWidgetItem(
                        product["category"] or ""
                    ),  # Category (or empty string if None)
                )
                self.product_table.setItem(
                    row_idx,
                    3,
                    QTableWidgetItem(product["description"] or ""),  # Description
                )
                self.product_table.setItem(
                    row_idx,
                    4,
                    QTableWidgetItem(
                        f"{product['purchase_price']:.2f} DZD"
                    ),  # Purchase Price (formatted)
                )
                self.product_table.setItem(
                    row_idx,
                    5,
                    QTableWidgetItem(
                        f"{product['selling_price']:.2f} DZD"
                    ),  # Selling Price (formatted)
                )
                self.product_table.setItem(
                    row_idx,
                    6,
                    QTableWidgetItem(
                        str(product["quantity_in_stock"])
                    ),  # Stock Quantity
                )

            # Update column visibility based on self.visible_columns
            for col_idx in range(self.product_table.columnCount()):
                self.product_table.setColumnHidden(
                    col_idx,
                    col_idx
                    not in self.visible_columns,  # Hide column if its index is not in visible_columns
                )
        except Exception as e:  # Catch any errors during product loading
            self.show_error(
                "Erreur Chargement Produits", f"Impossible de charger les produits: {e}"
            )

    def filter_products(self):
        """
        Triggered when the search input or category filter changes.
        Calls load_products to refresh the table based on new filter criteria.
        """
        self.load_products()

    def on_row_selected(self):
        """
        Called when a row in the product table is selected.
        Populates the input form with the data of the selected product.
        Enables/disables CRUD buttons based on selection.
        """
        selected_items = (
            self.product_table.selectedItems()
        )  # Get currently selected items
        if selected_items:  # If any items are selected (i.e., a row is selected)
            selected_row = (
                self.product_table.currentRow()
            )  # Get the index of the selected row
            # Get product ID from the first column of the selected row
            self.current_product_id = int(
                self.product_table.item(selected_row, 0).text()
            )
            # Populate form fields with data from the selected row
            self.name_input.setText(self.product_table.item(selected_row, 1).text())
            self.category_input.setText(
                self.product_table.item(selected_row, 2).text() or ""  # Category
            )
            self.description_input.setPlainText(
                self.product_table.item(selected_row, 3).text() or ""  # Description
            )
            # Safely parse purchase price (string to float)
            try:
                purchase_price_text = (
                    self.product_table.item(selected_row, 4)  # Get text from cell
                    .text()
                    .replace(" DZD", "")  # Remove currency suffix
                    .replace(",", ".")  # Replace comma with dot for float conversion
                )
                self.purchase_price_input.setValue(float(purchase_price_text))
            except ValueError:  # If conversion fails, set to 0.0
                self.purchase_price_input.setValue(0.0)
            # Safely parse selling price
            try:
                selling_price_text = (
                    self.product_table.item(selected_row, 5)
                    .text()
                    .replace(" DZD", "")
                    .replace(",", ".")
                )
                self.selling_price_input.setValue(float(selling_price_text))
            except ValueError:
                self.selling_price_input.setValue(0.0)

            # Enable Update and Delete buttons, disable Add button
            if self.update_button:
                self.update_button.setEnabled(True)
            if self.delete_button:
                self.delete_button.setEnabled(True)
            if self.add_button:
                self.add_button.setEnabled(
                    False
                )  # Cannot add when a product is selected for editing
        else:  # If no row is selected (e.g., selection cleared)
            self.clear_form()  # Clear the form and reset button states

    def clear_form(self):
        """
        Clears all input fields in the form, resets the current_product_id,
        clears table selection, and resets CRUD button states.
        """
        self.current_product_id = None  # No product is selected
        # Clear all input fields
        self.name_input.clear()
        self.category_input.clear()
        self.description_input.clear()
        self.purchase_price_input.setValue(0.0)
        self.selling_price_input.setValue(0.0)
        if self.product_table:  # If the table exists
            self.product_table.clearSelection()  # Clear any selection in the table

        # Reset button states: Update/Delete disabled, Add enabled
        if self.update_button:
            self.update_button.setEnabled(False)
        if self.delete_button:
            self.delete_button.setEnabled(False)
        if self.add_button:
            self.add_button.setEnabled(True)

    def show_column_menu(self, position):
        """
        Displays a context menu for the table header, allowing users to show/hide columns.
        Args:
            position: The position where the context menu was requested (usually mouse click position).
        """
        menu = QMenu(self)  # Create a new context menu
        header = (
            self.product_table.horizontalHeader()
        )  # Get the table's horizontal header

        # Iterate through each column in the header
        for column in range(header.count()):
            column_name = self.product_table.horizontalHeaderItem(
                column
            ).text()  # Get column name
            action = QAction(
                column_name, self, checkable=True
            )  # Create a checkable action for this column
            action.setChecked(
                column in self.visible_columns
            )  # Check it if the column is currently visible
            # Connect the action's triggered signal to toggle_column_visibility method
            # Use a lambda function to pass the column index and checked state
            action.triggered.connect(
                lambda checked, col=column: self.toggle_column_visibility(col, checked)
            )
            menu.addAction(action)  # Add the action to the menu
        menu.exec(
            header.mapToGlobal(position)
        )  # Display the menu at the global cursor position

    def toggle_column_visibility(self, column, visible):
        """
        Toggles the visibility of a specified column in the product table.
        Updates the self.visible_columns list.
        Args:
            column (int): The index of the column to toggle.
            visible (bool): True to show the column, False to hide it.
        """
        if visible:  # If the action is to make the column visible
            if column not in self.visible_columns:  # And it's not already in the list
                self.visible_columns.append(column)  # Add it to the list
        else:  # If the action is to hide the column
            if column in self.visible_columns:  # And it's currently in the list
                self.visible_columns.remove(column)  # Remove it from the list
        self.product_table.setColumnHidden(
            column, not visible
        )  # Update table's column visibility
        self.visible_columns.sort()  # Keep the list of visible columns sorted (optional, for consistency)


if (
    __name__ == "__main__"
):  # This block executes if the script is run directly (for testing)
    import sys  # For system-specific parameters and functions
    from PyQt6.QtWidgets import QApplication  # Application class
    from database.database import (
        initialize_database,
        add_product,
        get_all_products,
    )  # DB functions for testing
    from theme import apply_global_style  # Function to apply global theme

    initialize_database()  # Ensure the database and tables exist
    # Add some sample products if the database is empty, for testing purposes
    if not get_all_products():
        add_product(
            "Ordinateur Portable",  # Name
            "Puissant pour le travail",  # Description
            "Électronique",  # Category
            750.0,  # Purchase price
            999.99,  # Selling price
            10,  # Initial stock (though ProductView itself doesn't handle initial stock input)
        )
        add_product(
            "Souris Gamer",
            "Haute précision",
            "Accessoires Informatique",
            25.0,
            49.90,
            50,
        )

    app = QApplication(sys.argv)  # Create the application instance
    apply_global_style(app)  # Apply the global theme to the application
    product_widget = ProductView()  # Create an instance of the ProductView
    product_widget.show()  # Display the ProductView widget
    sys.exit(app.exec())  # Start the Qt event loop
