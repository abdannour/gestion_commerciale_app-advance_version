# Updated content for sidou2/views/stock_view.py
import sys  # Standard Python library for system-specific parameters and functions.
import os  # Standard Python library for interacting with the operating system, e.g., for path manipulation.
import csv  # Standard Python library for working with CSV files.
from PyQt6.QtWidgets import (  # Import necessary UI components from PyQt6.
    QWidget,  # Base class for all UI objects.
    QVBoxLayout,  # Arranges widgets vertically.
    QHBoxLayout,  # Arranges widgets horizontally.
    QLabel,  # Displays text or images.
    QLineEdit,  # Allows single-line text input.
    QPushButton,  # Represents a command button.
    QTableWidget,  # Provides a table display.
    QTableWidgetItem,  # Represents an item in a QTableWidget.
    QMessageBox,  # Displays modal dialogs for messages (info, warning, error).
    QHeaderView,  # Provides header rows or columns for item views like QTableWidget.
    QAbstractItemView,  # Provides an abstract model for item views.
    QComboBox,  # Provides a dropdown list of items.
    QApplication,  # Manages the application's control flow and main settings.
    QFrame,  # Provides a frame, often used as a container or for styling.
    QGridLayout,  # Arranges widgets in a grid layout.
    QFileDialog,  # Provides a dialog for opening and saving files.
)
from PyQt6.QtCore import (
    Qt,
    QSize,
)  # Import core Qt functionalities like alignment flags and size objects.
from PyQt6.QtGui import (
    QColor,
    QIcon,
    QPixmap,
    QFont,
)  # Import classes for graphical elements like colors, icons, and fonts.

# Import custom theme settings (styles, colors, fonts, icon directory, etc.).
from theme import (
    STYLES,
    COLORS,
    FONTS,
    ICON_DIR,
    STOCK_COLORS,
    RADIUS,
    SPACING,
)  # Added SPACING

# Import database interaction functions (search_products, get_all_categories).
from database.database import search_products, get_all_categories
from .base_view import BaseView  # Import BaseView for common UI functionalities.
from utils.error_handler import DatabaseError  # Import custom DatabaseError exception.

# Define a threshold for considering stock as "low".
LOW_STOCK_THRESHOLD = 5


class StockView(BaseView):  # StockView class inherits from BaseView.
    def __init__(self):
        """
        Constructor for the StockView.
        Initializes the UI for managing and displaying stock information.
        """
        super().__init__(
            "Gestion des Stocks"
        )  # Call BaseView's constructor with the window title.
        # Apply main window style for background consistency (handled by BaseView).
        self._init_ui_elements()  # Initialize UI elements specific to this view.
        self.load_categories_filter()  # Load categories into the filter dropdown.
        self.load_stock_data()  # Perform an initial load of stock data with default filters.

    def _init_ui_elements(self):  # Renamed from init_ui to avoid potential conflicts.
        """
        Initializes the user interface elements of the StockView.
        Sets up filter controls, the stock display table, and action buttons.
        """
        self.create_title()  # Use BaseView's method to create and display the view title.

        # --- Filter Card Section ---
        # Create a QFrame to act as a styled card for filter controls.
        filter_card = QFrame()
        filter_card.setObjectName(
            "filterCard"
        )  # Set object name for specific styling via QSS.
        # Apply card style from the theme, with fallbacks if the style is not defined.
        filter_card.setStyleSheet(
            STYLES.get(
                "card",
                f"""
            QFrame#filterCard {{
                background-color: {COLORS.get('surface', '#ffffff')};
                border-radius: {RADIUS.get('lg', '12px')};
                padding: {SPACING.get('xl', '20px')};
                border: 1px solid {COLORS.get('border', '#e0e0e0')};
            }}
            """,
            )
        )
        # Create a grid layout for arranging filter elements within the card.
        filter_layout = QGridLayout(filter_card)
        filter_layout.setSpacing(
            int(SPACING.get("md", "12px").replace("px", ""))
        )  # Set spacing between grid cells.

        # Create and configure the search input field.
        search_label = QLabel("Rechercher:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Nom du produit, catégorie..."
        )  # Placeholder text for guidance.
        self.search_input.textChanged.connect(
            self.filter_stock_data
        )  # Connect text changes to the filtering function.

        # Create and configure the category filter dropdown.
        category_label = QLabel("Catégorie:")
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.currentIndexChanged.connect(
            self.filter_stock_data
        )  # Connect selection changes to filtering.

        # Create and configure the stock level filter dropdown.
        stock_level_label = QLabel("Niveau de Stock:")
        self.stock_level_filter_combo = QComboBox()
        self.stock_level_filter_combo.addItems(  # Add predefined stock level options.
            [
                "Tous les niveaux",
                f"Stock Faible (≤ {LOW_STOCK_THRESHOLD})",
                "En Stock (> 0)",
                "Hors Stock (0)",
            ]
        )
        self.stock_level_filter_combo.currentIndexChanged.connect(
            self.filter_stock_data
        )  # Connect selection changes to filtering.

        # Apply common styles to filter labels and input widgets using BaseView methods.
        self.apply_label_styles([search_label, category_label, stock_level_label])
        self.apply_input_styles(
            [
                self.search_input,
                self.category_filter_combo,
                self.stock_level_filter_combo,
            ]
        )

        # Add filter widgets to the grid layout with specified row and column positions.
        filter_layout.addWidget(search_label, 0, 0)  # Row 0, Col 0.
        filter_layout.addWidget(
            self.search_input, 0, 1, 1, 2  # Row 0, Col 1, spans 1 row, 2 columns.
        )
        filter_layout.addWidget(category_label, 1, 0)  # Row 1, Col 0.
        filter_layout.addWidget(self.category_filter_combo, 1, 1)  # Row 1, Col 1.
        filter_layout.addWidget(stock_level_label, 1, 2)  # Row 1, Col 2.
        filter_layout.addWidget(self.stock_level_filter_combo, 1, 3)  # Row 1, Col 3.

        # Set column stretch factors to manage how space is distributed.
        filter_layout.setColumnStretch(
            1, 2  # Column 1 (search input area) gets more stretch.
        )
        filter_layout.setColumnStretch(3, 1)  # Column 3 (stock level filter) gets less.

        self.main_layout.addWidget(
            filter_card
        )  # Add the filter card to the main view layout.

        # --- Stock Table Section ---
        # Create the table to display stock information using BaseView's helper method.
        self.stock_table = self.create_table(
            [
                "ID Produit",
                "Nom",
                "Catégorie",
                "Quantité en Stock",
            ]  # Define table column headers.
        )
        # Configure how columns resize.
        self.stock_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch  # Stretch most columns to fill available width.
        )
        self.stock_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,  # Resize ID column to fit content.
        )
        self.stock_table.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,  # Resize Quantity column to fit content.
        )
        self.main_layout.addWidget(
            self.stock_table
        )  # Add the table to the main view layout.

        # --- Button Layout Section ---
        # Create a horizontal layout for action buttons using BaseView's method.
        button_layout = self.create_button_layout()
        button_layout.addStretch()  # Add stretch to push buttons to the right (or distribute space).

        # Create the "Exporter CSV" button.
        self.export_button = self.create_button(
            "Exporter CSV",
            self.export_stock_data,
            style_key="button_secondary",  # Text, callback, style.
        )
        # Set an icon for the export button.
        export_icon_path = os.path.join(
            ICON_DIR,
            "file-arrow-down-svgrepo-com.svg",  # Path to a generic download icon.
        )
        if os.path.exists(export_icon_path):
            self.export_button.setIcon(QIcon(export_icon_path))
        else:
            print(f"Icon not found: {export_icon_path}")  # Log if icon is missing.
        self.export_button.setIconSize(QSize(18, 18))  # Set icon dimensions.

        # Create the "Rafraîchir" (Refresh) button.
        self.refresh_button = self.create_button(
            "Rafraîchir", self.load_stock_data_with_filters, style_key="button_primary"
        )
        # Set an icon for the refresh button.
        refresh_icon_path = os.path.join(ICON_DIR, "refresh-svgrepo-com.svg")
        if os.path.exists(refresh_icon_path):
            self.refresh_button.setIcon(QIcon(refresh_icon_path))
        self.refresh_button.setIconSize(QSize(18, 18))

        # Add buttons to the button layout.
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.refresh_button)
        self.main_layout.addLayout(
            button_layout
        )  # Add button layout to the main view layout.

    def load_stock_data(
        self,
        # Default parameters are illustrative; actual values are read from UI elements.
        # search_term="",
        # category_filter="Toutes les catégories",
        # stock_level_filter="Tous les niveaux",
    ):
        """
        Loads stock data from the database based on current filter settings
        and populates the stock table.
        Applies conditional styling to rows based on stock quantity.
        """
        # Get current filter values from the UI input elements.
        search_query = self.search_input.text().strip()
        category = self.category_filter_combo.currentText()
        # Treat "Toutes les catégories" or invalid index as no specific category filter.
        if (
            category == "Toutes les catégories"
            or self.category_filter_combo.currentIndex()
            == -1  # -1 indicates no item selected or empty combo.
        ):
            category = None  # Pass None to database function for no category filter.
        stock_level_filter_text = self.stock_level_filter_combo.currentText()

        self.stock_table.setRowCount(0)  # Clear existing rows from the table.
        try:
            # Search products based on search query and category.
            products = search_products(search_query, category)
            filtered_products = []  # List to hold products after stock level filtering.

            # Apply stock level filtering based on the selected option.
            if stock_level_filter_text == f"Stock Faible (≤ {LOW_STOCK_THRESHOLD})":
                filtered_products = [
                    p
                    for p in products  # List comprehension for filtering.
                    if 0
                    < p["quantity_in_stock"]
                    <= LOW_STOCK_THRESHOLD  # Products with stock > 0 and <= threshold.
                ]
            elif stock_level_filter_text == "En Stock (> 0)":
                filtered_products = [p for p in products if p["quantity_in_stock"] > 0]
            elif stock_level_filter_text == "Hors Stock (0)":
                filtered_products = [p for p in products if p["quantity_in_stock"] == 0]
            else:  # "Tous les niveaux" or any other case.
                filtered_products = products  # No stock level filtering applied.

            self.stock_table.setRowCount(
                len(filtered_products)
            )  # Set table rows to the number of filtered products.
            for row_idx, product in enumerate(
                filtered_products
            ):  # Iterate through filtered products.
                stock_qty = product["quantity_in_stock"]  # Get current stock quantity.
                # Create QTableWidgetItem for each piece of product data.
                item_id = QTableWidgetItem(str(product["id"]))
                item_name = QTableWidgetItem(product["name"])
                item_category = QTableWidgetItem(
                    product["category"] or ""
                )  # Use empty string if category is None.
                item_stock = QTableWidgetItem(str(stock_qty))
                item_stock.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )  # Center-align stock quantity.

                # Determine row styling based on stock quantity.
                status_style = None
                if stock_qty == 0:
                    status_style = STOCK_COLORS[
                        "out_of_stock"
                    ]  # Style for out-of-stock items.
                elif stock_qty <= LOW_STOCK_THRESHOLD:
                    status_style = STOCK_COLORS[
                        "low_stock"
                    ]  # Style for low-stock items.
                else:
                    status_style = STOCK_COLORS[
                        "normal_stock"
                    ]  # Style for normal stock items.

                # Set items in the table row.
                self.stock_table.setItem(row_idx, 0, item_id)
                self.stock_table.setItem(row_idx, 1, item_name)
                self.stock_table.setItem(row_idx, 2, item_category)
                self.stock_table.setItem(row_idx, 3, item_stock)

                # Apply conditional row styling if a status_style is determined.
                if status_style:
                    base_bg_color = QColor(
                        status_style["bg"]
                    )  # Base background color from theme.
                    # Apply a slightly lighter background for alternating rows (zebra striping).
                    row_bg_color = (
                        base_bg_color.lighter(110)  # Make odd rows 10% lighter.
                        if row_idx % 2 == 1  # Check if row index is odd.
                        else base_bg_color
                    )

                    # Apply background and text color to all cells in the row.
                    for col in range(self.stock_table.columnCount()):
                        cell = self.stock_table.item(row_idx, col)
                        if cell:  # Ensure cell item exists.
                            cell.setBackground(row_bg_color)
                            if (
                                col == 3
                            ):  # Special styling for the stock quantity column.
                                cell.setForeground(
                                    QColor(status_style["text"])
                                )  # Set text color.
                                font = cell.font()  # Get current font.
                                font.setBold(True)  # Make text bold.
                                cell.setFont(font)  # Apply modified font.
        except (
            Exception
        ) as e:  # Catch any exceptions during data loading or processing.
            # Show a critical error message to the user.
            QMessageBox.critical(
                self, "Erreur Stock", f"Impossible de charger les données de stock: {e}"
            )

    def export_stock_data(self):
        """
        Exports the current data from the stock table to a CSV file.
        Prompts the user for a file path and name.
        """
        if self.stock_table.rowCount() == 0:  # Check if there's any data to export.
            QMessageBox.information(self, "Export", "Aucune donnée à exporter.")
            return

        # Open a file dialog to get the desired save path from the user.
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Stock CSV",
            "stock_export.csv",
            "CSV Files (*.csv)",  # Dialog title, default filename, file type filter.
        )
        if path:  # If a valid path was chosen.
            try:
                # Open the file in write mode with UTF-8 encoding.
                with open(path, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(
                        csvfile, delimiter=";"
                    )  # Create a CSV writer with semicolon delimiter.
                    # Write table headers to the CSV file.
                    headers = [
                        self.stock_table.horizontalHeaderItem(
                            col
                        ).text()  # Get header text for each column.
                        for col in range(self.stock_table.columnCount())
                    ]
                    writer.writerow(headers)
                    # Write table row data to the CSV file.
                    for row in range(self.stock_table.rowCount()):
                        row_data = [
                            (
                                self.stock_table.item(
                                    row, col
                                ).text()  # Get text from each cell.
                                if self.stock_table.item(
                                    row, col
                                )  # Check if item exists.
                                else ""  # Use empty string for empty cells.
                            )
                            for col in range(self.stock_table.columnCount())
                        ]
                        writer.writerow(row_data)
                # Show a success message using BaseView's method.
                self.show_info("Exportation Réussie", f"Données exportées vers {path}")
            except Exception as e:  # Catch any errors during file writing.
                # Show an error message using BaseView's method.
                self.show_error(
                    "Erreur d'Exportation", f"Impossible d'exporter les données: {e}"
                )

    def load_categories_filter(self):
        """
        Loads product categories from the database and populates the category filter dropdown.
        Uses BaseView's populate_category_combo method.
        """
        self.populate_category_combo(self.category_filter_combo)

    def load_stock_data_with_filters(self):
        """
        Reloads stock data using the current values from all filter controls.
        This is typically connected to the "Refresh" button.
        """
        self.load_stock_data()  # Calling load_stock_data automatically uses current filter values.

    def filter_stock_data(self):
        """
        This method is connected to the textChanged and currentIndexChanged signals
        of the filter input fields. It triggers a reload of the stock data,
        which in turn applies the new filter values.
        """
        self.load_stock_data()  # Reloads data, implicitly applying filters.
