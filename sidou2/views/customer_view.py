# Updated content for sidou2/views/customer_view.py
import datetime  # Import the datetime module to work with dates and times
from PyQt6.QtWidgets import (  # Import necessary widgets from PyQt6
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,  # Added QGroupBox for better UI organization
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)  # Import Qt core functionalities like signals and alignment

# Import custom theme elements (colors, fonts, spacing, radius, and predefined styles)
from theme import COLORS, FONTS, SPACING, RADIUS, STYLES
from database.database import (  # Import database functions for customer and sales data
    get_all_customers,
    add_customer,
    update_customer,
    delete_customer,
    get_sales_by_customer,
    get_sale_items,
)

# Import BaseView for common view functionalities
from views.base_view import BaseView


class CustomerView(BaseView):  # CustomerView class inherits from BaseView
    """
    Manages the customer anagement interface.
    Allows users to add, update, delete, and view customer information,
    as well as view their purchase history.
    This class is part of a group project for a university presentation,
    demonstrating GUI design and database interaction.
    """

    # Define a signal that is emitted when customer data is updated
    customer_updated = pyqtSignal()

    def __init__(self):
        """
        Constructor for the CustomerView.
        Initializes the UI and loads initial customer data.
        """
        super().__init__(
            "Gestion des Clients"
        )  # Call the BaseView constructor, passing the window title
        self.current_customer_id = (
            None  # Variable to store the ID of the currently selected customer
        )
        # Initialize UI elements specific to the customer view
        self.init_ui_customer()  # Renamed to avoid potential clash if BaseView.init_ui grows
        self.load_customers()  # Load existing customers into the table

    def init_ui_customer(
        self,
    ):  # Changed from init_ui to avoid override issues if BaseView has its own init_ui
        """
        Initializes the user interface elements for the customer view.
        Sets up the layout, input fields, buttons, and table.
        """
        # Create the main title for this view using the BaseView's method
        self.create_title("Gestion des Clients")  # Using BaseView method

        # --- Form Layout for Customer Input Fields ---
        # Use BaseView's create_form_widget for a themed container (e.g., a card-like frame)
        form_container, form_layout = self.create_form_widget()

        # Create QLineEdit widgets for customer information input
        self.name_input = QLineEdit()  # Input field for customer name
        self.name_input.setPlaceholderText(
            "Nom du client*"
        )  # Placeholder text indicating it's a required field
        self.address_input = QLineEdit()  # Input field for customer address
        self.address_input.setPlaceholderText("Adresse")  # Placeholder text
        self.phone_input = QLineEdit()  # Input field for customer phone number
        self.phone_input.setPlaceholderText("Téléphone")  # Placeholder text
        self.email_input = QLineEdit()  # Input field for customer email
        self.email_input.setPlaceholderText("Email")  # Placeholder text

        # Apply predefined styles (from theme.py) to the input fields using a BaseView helper method
        self.apply_input_styles(
            [self.name_input, self.address_input, self.phone_input, self.email_input]
        )

        # Add labels and corresponding input fields to the form_layout (a QGridLayout)
        form_layout.addWidget(
            QLabel("Nom:"), 0, 0
        )  # Label for Name, at grid row 0, col 0
        form_layout.addWidget(
            self.name_input, 0, 1
        )  # Name input field, at grid row 0, col 1
        form_layout.addWidget(QLabel("Adresse:"), 1, 0)  # Label for Address
        form_layout.addWidget(self.address_input, 1, 1)  # Address input field
        form_layout.addWidget(QLabel("Tél:"), 0, 2)  # Label for Phone
        form_layout.addWidget(self.phone_input, 0, 3)  # Phone input field
        form_layout.addWidget(QLabel("Email:"), 1, 2)  # Label for Email
        form_layout.addWidget(self.email_input, 1, 3)  # Email input field

        # Apply styles to all QLabel widgets within the form_container
        labels_in_form = [
            child for child in form_container.findChildren(QLabel)
        ]  # Get all QLabels
        self.apply_label_styles(
            labels_in_form, "label_bold"
        )  # Make form labels bold using a theme style

        # Add the styled form_container (with its grid layout) to the main_layout of the CustomerView
        self.main_layout.addWidget(form_container)

        # --- Button Layout for CRUD Operations (Create, Read, Update, Delete) ---
        # Use BaseView's helper method to create standard CRUD buttons and a clear button
        self.add_button, self.update_button, self.delete_button, self.clear_button = (
            self.create_crud_buttons(
                add_handler=self.add_new_customer,  # Function to call when 'Add' is clicked
                update_handler=self.update_selected_customer,  # Function for 'Update'
                delete_handler=self.delete_selected_customer,  # Function for 'Delete'
                clear_handler=self.clear_form,  # Function for 'Clear Form'
            )
        )

        # Add "View History" button separately as it's specific to this view
        history_button_layout = (
            self.create_button_layout()
        )  # Get a themed QHBoxLayout from BaseView
        self.history_button = self.create_button(
            "Voir Historique Achats",  # Button text
            callback=self.show_customer_history,  # Function to call
            enabled=False,  # Initially disabled
            style_key="button_secondary",
        )  # Style from theme.py
        history_button_layout.addStretch()  # Add stretch to push button to the right (if desired)
        history_button_layout.addWidget(self.history_button)  # Add button to its layout
        self.main_layout.addLayout(
            history_button_layout
        )  # Add this layout to the main view layout

        # --- Customer Table ---
        # Create the table to display customer data using BaseView's helper method
        self.customer_table = self.create_table(  # Use BaseView method
            columns=[
                "ID",
                "Nom",
                "Adresse",
                "Téléphone",
                "Email",
            ]  # Define column headers
        )
        # Set resize mode for the 'ID' column to fit its content
        self.customer_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        # Connect the table's item selection change signal to the on_row_selected method
        self.customer_table.itemSelectionChanged.connect(self.on_row_selected)
        # Add the customer table to the main layout of the view
        self.main_layout.addWidget(self.customer_table)

        # self.setLayout(main_layout) # setLayout is done by BaseView automatically for self.main_layout

    def load_customers(self):
        """
        Loads customer data from the database and populates the customer_table.
        Clears the form fields after loading.
        Handles potential errors during database interaction.
        """
        self.customer_table.setRowCount(0)  # Clear existing rows from the table
        try:
            customers = get_all_customers()  # Fetch all customers from the database
            if customers:  # If there are customers
                self.customer_table.setRowCount(
                    len(customers)
                )  # Set the number of rows in the table
                for row_idx, customer in enumerate(
                    customers
                ):  # Iterate through each customer
                    # Populate table cells with customer data
                    self.customer_table.setItem(
                        row_idx, 0, QTableWidgetItem(str(customer["id"]))
                    )  # ID
                    self.customer_table.setItem(
                        row_idx, 1, QTableWidgetItem(customer["name"])
                    )  # Name
                    self.customer_table.setItem(
                        row_idx, 2, QTableWidgetItem(customer["address"] or "")
                    )  # Address (or empty string if None)
                    self.customer_table.setItem(
                        row_idx, 3, QTableWidgetItem(customer["phone"] or "")
                    )  # Phone
                    self.customer_table.setItem(
                        row_idx, 4, QTableWidgetItem(customer["email"] or "")
                    )  # Email
            self.clear_form()  # Reset the input form fields
        except Exception as e:  # Catch any exceptions during the process
            # Show an error message using BaseView's helper method
            self.show_error("Erreur", f"Erreur lors du chargement des clients: {e}")

    def on_row_selected(self):
        """
        Handles the event when a row is selected in the customer_table.
        Populates the form fields with the data of the selected customer.
        Enables/disables CRUD buttons based on selection.
        """
        selected_items = (
            self.customer_table.selectedItems()
        )  # Get currently selected items
        if selected_items:  # If any item is selected (i.e., a row is selected)
            selected_row = (
                self.customer_table.currentRow()
            )  # Get the index of the selected row
            # Store the ID of the selected customer (from the first column)
            self.current_customer_id = int(
                self.customer_table.item(selected_row, 0).text()
            )
            # Populate input fields with data from the selected row
            self.name_input.setText(self.customer_table.item(selected_row, 1).text())
            self.address_input.setText(self.customer_table.item(selected_row, 2).text())
            self.phone_input.setText(self.customer_table.item(selected_row, 3).text())
            self.email_input.setText(self.customer_table.item(selected_row, 4).text())

            # Enable Update, Delete, and View History buttons as a customer is now selected
            if self.update_button:
                self.update_button.setEnabled(True)
            if self.delete_button:
                self.delete_button.setEnabled(True)
            if self.history_button:
                self.history_button.setEnabled(True)
            # Disable the Add button as we are in "edit mode" for the selected customer
            if self.add_button:
                self.add_button.setEnabled(False)
        else:
            # If no row is selected (e.g., selection cleared), reset the form
            self.clear_form()

    def clear_form(self):
        """
        Clears all input fields and resets the current_customer_id.
        Resets button states to default (Add enabled, others disabled).
        Clears any selection in the customer_table.
        """
        self.current_customer_id = None  # No customer is selected
        # Clear text from all input fields
        self.name_input.clear()
        self.address_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        if self.customer_table:
            self.customer_table.clearSelection()  # Clear table selection

        # Reset button states
        if self.update_button:
            self.update_button.setEnabled(False)  # Disable Update
        if self.delete_button:
            self.delete_button.setEnabled(False)  # Disable Delete
        if self.history_button:
            self.history_button.setEnabled(False)  # Disable View History
        if self.add_button:
            self.add_button.setEnabled(True)  # Enable Add

    def add_new_customer(self):
        """
        Adds a new customer to the database using the data from the form fields.
        Validates that the name field is not empty.
        Reloads customer list and emits a signal upon successful addition.
        Displays appropriate messages (success or error).
        """
        # Get text from input fields, stripping leading/trailing whitespace
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        if not name:  # Check if the name field is empty
            # Show a warning message using BaseView's helper method
            self.show_warning("Attention", "Le nom du client est obligatoire.")
            return  # Stop further execution

        try:
            # Call the database function to add the customer
            add_customer(name, phone, email, address)
            self.clear_form()  # Reset the form
            self.load_customers()  # Reload the customer list in the table
            self.customer_updated.emit()  # Emit a signal indicating customer data has changed
            # Show a success message
            self.show_info("Succès", "Le client a été ajouté avec succès.")
        except Exception as e:  # Catch any errors during the process
            # Show an error message
            self.show_error("Erreur", f"Erreur lors de l'ajout du client: {e}")

    def update_selected_customer(self):
        """
        Updates the currently selected customer's information in the database.
        Requires a customer to be selected (current_customer_id must not be None).
        Validates that the name field is not empty.
        Reloads customer list and emits a signal upon successful update.
        """
        if not self.current_customer_id:  # Check if a customer is selected
            self.show_warning(
                "Attention", "Veuillez sélectionner un client à modifier."
            )
            return

        # Get updated data from input fields
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        if not name:  # Ensure name is not empty
            self.show_warning("Attention", "Le nom du client est obligatoire.")
            return

        try:
            # Call the database function to update the customer
            update_customer(self.current_customer_id, name, phone, email, address)
            self.load_customers()  # Reload customer list
            self.customer_updated.emit()  # Emit signal
            self.show_info(
                "Succès", "Le client a été modifié avec succès."
            )  # Show success message
        except Exception as e:  # Catch errors
            self.show_error(
                "Erreur", f"Erreur lors de la modification du client: {e}"
            )  # Show error message

    def delete_selected_customer(self):
        """
        Deletes the currently selected customer from the database.
        Requires a customer to be selected.
        Asks for user confirmation before deletion.
        Reloads customer list and emits a signal upon successful deletion.
        """
        if not self.current_customer_id:  # Check if a customer is selected
            self.show_warning(
                "Attention", "Veuillez sélectionner un client à supprimer."
            )
            return

        # Ask for confirmation using BaseView's confirmation dialog
        if self.show_confirmation(
            "Confirmation", "Êtes-vous sûr de vouloir supprimer ce client ?"
        ):
            try:
                # Call the database function to delete the customer
                delete_customer(self.current_customer_id)
                self.clear_form()  # Clear the form
                self.load_customers()  # Reload customer list
                self.customer_updated.emit()  # Emit signal
                self.show_info(
                    "Succès", "Le client a été supprimé avec succès."
                )  # Show success message
            except Exception as e:  # Catch errors
                self.show_error(
                    "Erreur", f"Erreur lors de la suppression du client: {e}"
                )  # Show error message

    def show_customer_history(self):
        """
        Displays a dialog showing the purchase history for the selected customer.
        Requires a customer to be selected.
        Fetches sales history for the customer and passes it to the CustomerHistoryDialog.
        """
        if self.current_customer_id is None:  # Check if a customer is selected
            self.show_warning(
                "Aucun Client Sélectionné",
                "Veuillez sélectionner un client dans la table.",
            )
            return

        customer_name = (
            self.name_input.text()
        )  # Get the name of the selected customer from the form
        try:
            # Fetch sales history for the current customer from the database
            sales_history = get_sales_by_customer(self.current_customer_id)
            # Create and show the history dialog
            dialog = CustomerHistoryDialog(
                self.current_customer_id,
                customer_name,
                sales_history,
                self,  # Pass ID, name, data, and parent
            )
            dialog.exec()  # Show the dialog modally
        except Exception as e:  # Catch errors
            self.show_error(
                "Erreur Historique Client", f"Impossible de charger l'historique: {e}"
            )


class CustomerHistoryDialog(QDialog):  # Dialog to display a customer's sales history
    """
    A dialog window that displays the sales history for a specific customer.
    It shows a table of sales with options to view details for each sale.
    """

    def __init__(self, customer_id, customer_name, sales_data, parent=None):
        """
        Constructor for CustomerHistoryDialog.
        Args:
            customer_id (int): The ID of the customer.
            customer_name (str): The name of the customer.
            sales_data (list): A list of dictionaries, each representing a sale.
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent)  # Call QDialog constructor
        self.setWindowTitle(
            f"Historique des Achats - {customer_name} (ID: {customer_id})"
        )  # Set window title
        self.setMinimumWidth(700)  # Set minimum dialog width
        self.setMinimumHeight(400)  # Set minimum dialog height
        self.selected_sale_id = (
            None  # To store the ID of a sale selected in the history table
        )

        layout = QVBoxLayout(self)  # Main vertical layout for the dialog
        # Set content margins using theme spacing values
        layout.setContentsMargins(
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
            int(SPACING["lg"].replace("px", "")),
        )
        layout.setSpacing(
            int(SPACING["md"].replace("px", ""))
        )  # Set spacing between widgets

        # Style the dialog background and text color using theme values
        self.setStyleSheet(
            f"background-color: {COLORS['background']}; color: {COLORS['text_primary']};"
        )

        # Title label for the dialog content
        title_label = QLabel(f"Historique pour {customer_name}:")
        title_label.setStyleSheet(
            STYLES.get(
                "subtitle",
                f"font-size: {FONTS['subtitle']}pt; font-weight: bold; color: {COLORS['text_primary']};",
            )
        )
        layout.addWidget(title_label)

        # Table to display sales history
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(
            3
        )  # Three columns: Sale ID, Date, Total Amount
        self.history_table.setHorizontalHeaderLabels(
            ["ID Vente", "Date", "Montant Total"]
        )
        self.history_table.setStyleSheet(
            STYLES.get("table", "")
        )  # Apply themed table style
        self.history_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # Make table read-only
        self.history_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )  # Select whole rows
        self.history_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )  # Allow only single row selection
        self.history_table.verticalHeader().setVisible(
            False
        )  # Hide vertical (row number) header
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )  # Stretch columns to fill width
        self.history_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )  # Sale ID column fits content
        # Connect double-click on table row to show sale details
        self.history_table.doubleClicked.connect(
            self.show_sale_details_action
        )  # Renamed for clarity
        # Connect selection change to enable/disable details button
        self.history_table.itemSelectionChanged.connect(
            self.on_history_row_selected_dialog
        )  # Renamed

        layout.addWidget(self.history_table)  # Add table to the layout
        self.populate_table(sales_data)  # Fill the table with sales data

        button_layout = QHBoxLayout()  # Horizontal layout for buttons at the bottom
        # Button to view details of the selected sale
        self.details_button = QPushButton("Voir Détails Vente Sélectionnée")
        self.details_button.setEnabled(False)  # Initially disabled
        self.details_button.clicked.connect(
            self.show_sale_details_action
        )  # Connect to show details method
        self.details_button.setStyleSheet(
            STYLES.get("button_secondary", "")
        )  # Apply themed style

        # Standard OK button to close the dialog
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(
            self.accept
        )  # self.accept() closes the dialog with QDialog.Accepted
        self.ok_button.setStyleSheet(
            STYLES.get("button_primary", "")
        )  # Apply themed style
        self.ok_button.setMinimumWidth(100)  # Set minimum button width

        button_layout.addWidget(self.details_button)  # Add details button
        button_layout.addStretch()  # Add stretch to push OK button to the right
        button_layout.addWidget(self.ok_button)  # Add OK button

        layout.addLayout(button_layout)  # Add button layout to the main dialog layout
        self.setLayout(layout)  # Set the main layout for the dialog

    def populate_table(self, sales_data):
        """
        Populates the history_table with the provided sales data.
        Args:
            sales_data (list): A list of sale records (dictionaries).
        """
        self.history_table.setRowCount(0)  # Clear existing rows
        if sales_data:  # If data is available
            self.history_table.setRowCount(len(sales_data))  # Set number of rows
            for row_idx, sale in enumerate(sales_data):  # Iterate through sales
                # Populate table cells for each sale
                self.history_table.setItem(
                    row_idx, 0, QTableWidgetItem(str(sale["id"]))
                )  # Sale ID
                date_str = sale["sale_date"]  # Get sale date string
                try:
                    # Attempt to parse and reformat the date for display
                    dt_obj = datetime.datetime.fromisoformat(date_str)
                    display_date = dt_obj.strftime("%Y-%m-%d %H:%M")
                except ValueError:  # If parsing fails, use the original string
                    display_date = date_str
                self.history_table.setItem(
                    row_idx, 1, QTableWidgetItem(display_date)
                )  # Sale Date
                # Sale Total Amount, formatted to 2 decimal places with currency symbol
                self.history_table.setItem(
                    row_idx, 2, QTableWidgetItem(f"{sale['total_amount']:.2f} DZD")
                )

    def on_history_row_selected_dialog(self):  # Renamed
        """
        Handles row selection in the sales history table within this dialog.
        Enables the 'View Details' button if a row is selected.
        Stores the ID of the selected sale.
        """
        selected_items = self.history_table.selectedItems()  # Get selected items
        if selected_items:  # If a row is selected
            selected_row = self.history_table.currentRow()  # Get selected row index
            self.selected_sale_id = int(
                self.history_table.item(selected_row, 0).text()
            )  # Store sale ID
            self.details_button.setEnabled(True)  # Enable details button
        else:  # If no row is selected
            self.selected_sale_id = None  # Clear stored sale ID
            self.details_button.setEnabled(False)  # Disable details button

    def show_sale_details_action(self):  # Renamed
        """
        Shows a dialog with detailed items for the selected sale.
        This is triggered by clicking the 'View Details' button or double-clicking a row.
        Imports SaleDetailsDialog from sale_view dynamically to avoid circular imports at module level.
        """
        if (
            self.selected_sale_id is None
        ):  # If no sale ID is stored (e.g., button clicked without selection)
            selected_items = (
                self.history_table.selectedItems()
            )  # Try to get current selection
            if not selected_items:
                return  # No selection, do nothing
            selected_row = self.history_table.currentRow()
            if selected_row < 0:
                return  # Should not happen if selected_items is not empty
            self.selected_sale_id = int(
                self.history_table.item(selected_row, 0).text()
            )  # Get ID from current row

        if self.selected_sale_id is not None:  # If a sale ID is available
            try:
                # Fetch detailed items for the selected sale from the database
                items = get_sale_items(self.selected_sale_id)
                from views.sale_view import (
                    SaleDetailsDialog,
                )  # Late import to prevent circular dependency issues

                # Create and show the SaleDetailsDialog
                details_dialog = SaleDetailsDialog(
                    self.selected_sale_id, items, self
                )  # Pass sale ID, items, and parent
                details_dialog.exec()  # Show dialog modally
            except (
                ImportError
            ):  # Handle case where SaleDetailsDialog cannot be imported
                QMessageBox.critical(
                    self, "Erreur Import", "Impossible d'importer SaleDetailsDialog."
                )
            except Exception as e:  # Catch any other errors
                QMessageBox.critical(
                    self,
                    "Erreur Détails Vente",
                    f"Impossible de charger les détails: {e}",
                )


# This block allows the CustomerView to be run standalone for testing purposes
if __name__ == "__main__":
    import sys  # For system-specific parameters and functions
    from PyQt6.QtWidgets import QApplication  # For managing the Qt application
    from database.database import (
        initialize_database,
    )  # For initializing the database if needed
    from theme import apply_global_style  # For applying the global application theme

    initialize_database()  # Ensure the database is initialized
    app = QApplication(sys.argv)  # Create the QApplication instance
    apply_global_style(app)  # Apply the global theme to the application
    customer_widget = CustomerView()  # Create an instance of CustomerView
    customer_widget.show()  # Display the CustomerView widget
    sys.exit(app.exec())  # Start the Qt application event loop
