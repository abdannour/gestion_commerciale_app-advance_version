# Updated content for sidou2/main.py
# Standard library imports for system-specific parameters and operating system functionalities.
import sys  # Provides access to system-specific parameters and functions, like command-line arguments. Essential for GUI applications.
import os  # Provides a way of using operating system dependent functionality like reading or writing to the file system. Used here for path manipulations (e.g., icon paths, database path).
import logging  # Import logging to enable logging functionality throughout the application.

# PyQt6 imports for building the graphical user interface.
# QtWidgets contains classes to create and manage UI elements.
from PyQt6.QtWidgets import (
    QApplication,  # Manages the GUI application's control flow and main settings.
    QMainWindow,  # Represents the main window of the application, providing a framework for building an application's user interface.
    QLabel,  # Used to display text or an image; can be used for titles, labels for input fields, etc.
    QWidget,  # Base class for all user interface objects (widgets). It can be used as a container for other widgets.
    QVBoxLayout,  # Lines up widgets vertically. Useful for structuring sections of a window.
    QHBoxLayout,  # Lines up widgets horizontally. Used for arranging elements side-by-side.
    QListWidget,  # Provides a list of items that can be selected, often used for navigation menus.
    QStackedWidget,  # Provides a stack of widgets where only one is visible at a time, enabling multi-page applications.
    QListWidgetItem,  # Represents an individual item in a QListWidget.
    QFrame,  # Base class for widgets that have a frame, can be used for visual grouping or as a base for custom widgets.
    QMessageBox,  # For confirmation dialogs
    QInputDialog,  # For typed confirmation
    QPushButton,  # For the delete button
    QSpacerItem,  # For layout spacing
    QSizePolicy,  # For layout spacing
    QLineEdit,  # For input dialog echo mode
)

# QtCore imports for core non-GUI functionalities.
from PyQt6.QtCore import (
    Qt,  # Contains various flags and enumerations (e.g., alignment flags, mouse buttons).
    QSize,  # Represents the size of a 2D object using integer point precision. Used here for icon sizes.
)

# QtGui imports for GUI-related classes that are not widgets.
from PyQt6.QtGui import (
    QIcon,
    QFont,
)  # QIcon for handling icons, QFont for managing font properties.

# --- Local Module Imports ---
# These imports bring in custom-coded parts of the application.

# Import database initialization function.
from database.database import (
    initialize_database,  # Function to set up the application's database schema if it doesn't exist.
    dangerously_delete_all_data,  # Import the new delete function
)

# Import theme-related variables and functions.
# This centralizes the application's appearance (colors, fonts, styles).
from theme import (
    STYLES,  # Dictionary of stylesheet strings for various UI components.
    COLORS,  # Dictionary defining the color palette of the application.
    FONTS,  # Dictionary defining font families, sizes, and weights.
    ICON_DIR,  # Directory path where icon files are stored.
    apply_global_style,  # Function to apply a global stylesheet to the application.
    SPACING,  # Import spacing
    RADIUS,  # Import radius
)

# Import different view modules for the application's sections.
# Each view represents a major functional area of the application (e.g., Customers, Products).
from views.customer_view import CustomerView
from views.product_view import ProductView
from views.purchase_view import PurchaseView
from views.sale_view import SaleView
from views.stock_view import StockView
from views.dashboard_view import DashboardView
from views.base_view import BaseView  # Import BaseView for SettingsView to inherit from
from utils.error_handler import logger  # Import logger


# --- SettingsView Class Definition (Added Here) ---
class SettingsView(BaseView):
    """
    A view for application settings, including dangerous operations
    like deleting all database information.
    """

    def __init__(self):
        super().__init__("Paramètres")  # Title for the Settings View
        self.init_ui_settings()

    def init_ui_settings(self):
        self.create_title("Paramètres et Administration")

        # Danger Zone Section
        danger_zone_group = QFrame()
        danger_zone_group.setObjectName("dangerZoneGroup")
        danger_zone_group.setStyleSheet(
            f"""
            QFrame#dangerZoneGroup {{
                background-color: {COLORS.get('error_bg', '#fef2f2')};
                border: 1px solid {COLORS.get('error', '#ef4444')};
                border-radius: {RADIUS.get('lg', '12px')};
                padding: {SPACING.get('xl', '20px')};
                margin-top: {SPACING.get('xl', '20px')};
            }}
        """
        )
        danger_layout = QVBoxLayout(danger_zone_group)

        danger_title = QLabel("Zone de Danger")
        danger_title.setStyleSheet(
            f"""
            font-size: {FONTS.get('xl', 16)}pt;
            font-weight: bold;
            color: {COLORS.get('error_dark', '#dc2626')};
            margin-bottom: {SPACING.get('md', '12px')};
        """
        )
        danger_layout.addWidget(danger_title)

        description_label = QLabel(
            "Attention : L'action suivante est irréversible et entraînera la suppression "
            "complète de toutes les données de l'application (clients, produits, ventes, achats, etc.)."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet(
            f"color: {COLORS.get('error_dark', '#dc2626')}; margin-bottom: {SPACING.get('lg', '16px')};"
        )
        danger_layout.addWidget(description_label)

        self.delete_all_data_button = QPushButton(
            "Supprimer Toutes les Données de la Base de Données"
        )
        # Style the button to be visually alarming
        delete_button_style = STYLES.get(
            "button_destructive",
            f"""
            QPushButton {{
                background-color: {COLORS.get('error', '#ef4444')};
                color: {COLORS.get('white', '#ffffff')};
                border: none;
                border-radius: {RADIUS.get('md', '8px')};
                padding: {SPACING.get('md', '12px')} {SPACING.get('lg', '16px')};
                font-weight: bold;
                font-size: {FONTS.get('button', 12)}pt;
                min-height: 40px;
            }}
            QPushButton:hover {{ background-color: {COLORS.get('error_dark', '#dc2626')}; }}
        """,
        )
        self.delete_all_data_button.setStyleSheet(delete_button_style)

        # Add an icon to the delete button
        warning_icon_path = os.path.join(
            ICON_DIR, "alert-triangle-svgrepo-com.svg"
        )  # Assuming you have a warning icon
        if os.path.exists(warning_icon_path):
            self.delete_all_data_button.setIcon(QIcon(warning_icon_path))
            self.delete_all_data_button.setIconSize(QSize(20, 20))
        else:
            logger.warning(
                f"Warning icon not found for delete button: {warning_icon_path}"
            )

        self.delete_all_data_button.clicked.connect(self.handle_delete_all_data)

        button_container_layout = QHBoxLayout()
        button_container_layout.addStretch(1)
        button_container_layout.addWidget(self.delete_all_data_button)
        button_container_layout.addStretch(1)
        danger_layout.addLayout(button_container_layout)

        self.main_layout.addWidget(danger_zone_group)
        self.main_layout.addStretch(1)  # Push content to the top

    def handle_delete_all_data(self):
        # Step 1: Initial Confirmation
        reply = self.show_message_custom(
            "Confirmation Suppression Totale (Étape 1/3)",
            "Êtes-vous absolument sûr de vouloir supprimer TOUTES les données ?\n"
            "Cette action est IRREVERSIBLE et toutes les informations seront perdues.",
            icon=QMessageBox.Icon.Critical,
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default_button=QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            self.show_info(
                "Opération Annulée", "La suppression des données a été annulée."
            )
            return

        # Step 2: Typed Confirmation
        confirm_text, ok = QInputDialog.getText(
            self,
            "Confirmation Suppression Totale (Étape 2/3)",
            "Pour confirmer, taper 'Y' ",
            QLineEdit.EchoMode.Normal,  # Use Normal EchoMode
            "",  # Initial text in input dialog
        )
        if not ok:  # User pressed cancel
            self.show_info(
                "Opération Annulée", "La suppression des données a été annulée."
            )
            return

        if confirm_text.strip().upper() != "Y":
            self.show_error(
                "Confirmation Incorrecte",
                "La phrase de confirmation n'a pas été correctement saisie. Opération annulée.",
            )
            return

        # Step 3: Backup Prompt
        backup_reply = self.show_message_custom(
            "Sauvegarde Recommandée (Étape 3/3)",
            "Il est fortement recommandé de sauvegarder votre base de données ('gestion_commerciale.db') avant de continuer.\n"
            "Avez-vous effectué une sauvegarde ou souhaitez-vous continuer sans sauvegarde ?",
            icon=QMessageBox.Icon.Warning,
            buttons=QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            default_button=QMessageBox.StandardButton.Cancel,
        )

        if backup_reply == QMessageBox.StandardButton.Cancel:
            self.show_info(
                "Opération Annulée", "La suppression des données a été annulée."
            )
            return
        elif (
            backup_reply == QMessageBox.StandardButton.No
        ):  # User chooses to continue without backup
            final_reply = self.show_message_custom(
                "Confirmation Finale",
                "Vous avez choisi de continuer sans sauvegarde. Dernière chance : êtes-vous sûr ?",
                icon=QMessageBox.Icon.Critical,
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                default_button=QMessageBox.StandardButton.No,
            )
            if final_reply != QMessageBox.StandardButton.Yes:
                self.show_info(
                    "Opération Annulée", "La suppression des données a été annulée."
                )
                return

        # If Yes, proceed to delete.

        try:
            logger.warning("Attempting to delete all database data.")
            dangerously_delete_all_data()
            logger.info("All database data has been deleted successfully.")
            self.show_info(
                "Succès",
                "Toutes les données de la base de données ont été supprimées. L'application va nécessiter un redémarrage ou une actualisation pour refléter les changements.",
            )
            # Potentially, disable parts of UI or force reload/restart if possible.
            # For simplicity, we'll just show a message. Views will likely error out or show empty until app restart or data refresh.
            # After deletion, many views will fail to load data. A good practice would be to
            # re-initialize views or even restart the application.
            # For now, we just inform the user.

            # Attempt to refresh current views if possible, or instruct user to restart
            main_window = self.window()
            if main_window and isinstance(main_window, MainWindow):
                # Re-load current view to reflect changes (it will likely be empty)
                current_idx = main_window.stacked_widget.currentIndex()
                main_window.change_page(current_idx)

        except Exception as e:
            logger.error(f"Failed to delete all database data: {e}", exc_info=True)
            self.show_error(
                "Erreur Critique", f"La suppression des données a échoué: {e}"
            )


class MainWindow(
    QMainWindow
):  # Main application window class, inherits from QMainWindow. This is the top-level container for the UI.
    def __init__(self):  # Constructor for the MainWindow.
        super().__init__()  # Call the constructor of the parent class (QMainWindow) to initialize it.
        self.setWindowTitle(
            "Gestion Commerciale et de Stock"
        )  # Set the title that appears in the window's title bar.
        self.setGeometry(
            100, 100, 1100, 750
        )  # Set the initial position (x, y) and size (width, height) of the window.

        # The global style is applied once to the QApplication instance in the `if __name__ == "__main__":` block.
        # This ensures that styles are applied consistently across the application.
        # apply_global_style(QApplication.instance()) # Applied once in __main__

        self.init_ui()  # Call the method to initialize the user interface components within the main window.

    def init_ui(self):  # Method to set up the user interface of the main window.
        # Create a central widget. In QMainWindow, the central widget is the area where primary content is displayed.
        main_widget = QWidget()
        # Apply a background color to the central content area.
        # This ensures the area behind the stacked_widget has the correct theme background.
        main_widget.setStyleSheet(f"background-color: {COLORS['background']};")

        # Create a horizontal layout for the main_widget. This will hold the navigation sidebar and the content area.
        main_layout = QHBoxLayout(main_widget)  # Set layout on main_widget directly.
        main_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove any default margins around the layout.
        main_layout.setSpacing(
            0
        )  # Remove any default spacing between widgets in the layout.

        # Set the main_widget (which now contains main_layout) as the central widget of the QMainWindow.
        self.setCentralWidget(main_widget)

        # --- Navigation List (Sidebar) ---
        # This QListWidget will serve as the navigation menu on the left side.
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(230)  # Set a fixed width for the sidebar.
        self.nav_list.setIconSize(
            QSize(28, 28)
        )  # Set the size for icons in the navigation list items.
        self.nav_list.setStyleSheet(
            STYLES.get("sidebar", "") + STYLES.get("sidebar_item", "")
        )  # Apply styles defined in theme.py for the sidebar and its items.
        # Connect the currentRowChanged signal (emitted when selection changes) to the change_page method.
        self.nav_list.currentRowChanged.connect(self.change_page)
        main_layout.addWidget(
            self.nav_list
        )  # Add the navigation list to the main horizontal layout.

        # --- Stacked Widget (Main Content Area) ---
        # QStackedWidget holds different "pages" (widgets), showing one at a time.
        # This is where the content for each navigation item will be displayed.
        self.stacked_widget = QStackedWidget()
        # Ensure the background of the stacked widget itself (if visible between pages or if pages have transparent areas) matches the theme.
        self.stacked_widget.setStyleSheet(f"background-color: {COLORS['background']};")
        main_layout.addWidget(
            self.stacked_widget
        )  # Add the stacked widget to the main horizontal layout, next to the sidebar.

        # --- Initialize Views ---
        # Create instances of all the different view classes. Each view is a QWidget (or subclass)
        # that represents a specific section of the application (e.g., Dashboard, Customers).
        self.dashboard_view = DashboardView()
        self.customer_view = CustomerView()
        self.product_view = ProductView()
        self.purchase_view = PurchaseView()
        self.sale_view = SaleView()
        self.stock_view = StockView()
        self.settings_view = SettingsView()  # Initialize SettingsView

        # --- Connect Signals from Views to Refresh Methods ---
        # This is crucial for data consistency across different parts of the application.
        # When data changes in one view (e.g., a new sale is recorded), other relevant views are notified to refresh their data.

        # If a sale is recorded, or a product is updated, or a purchase is recorded,
        # call `refresh_on_sale_purchase_product_change` to update relevant views like Dashboard, Product list, Stock, etc.
        self.sale_view.sale_recorded.connect(
            self.refresh_on_sale_purchase_product_change
        )
        self.product_view.product_updated.connect(
            self.refresh_on_sale_purchase_product_change
        )
        self.purchase_view.purchase_recorded.connect(
            self.refresh_on_sale_purchase_product_change
        )
        # If customer data is updated (e.g., new customer added, existing one modified),
        # call `refresh_customer_related_views` to update views that display customer information.
        self.customer_view.customer_updated.connect(self.refresh_customer_related_views)

        # --- Add Pages to Navigation and Stacked Widget ---
        # Populate the navigation list and the stacked widget with the initialized views.
        # Arguments for add_page: display name in sidebar, widget instance, icon file name.
        self.add_page(
            "Tableau de Bord",
            self.dashboard_view,
            "dashboard-svgrepo-com.svg",  # Dashboard page
        )
        self.add_page(
            "Clients", self.customer_view, "users-svgrepo-com.svg"
        )  # Customers page
        self.add_page(
            "Produits", self.product_view, "product-svgrepo-com.svg"
        )  # Products page
        self.add_page(
            "Achats", self.purchase_view, "shopping-bag-add-icon.svg"
        )  # Purchases page
        self.add_page("Ventes", self.sale_view, "sale-svgrepo-com.svg")  # Sales page
        self.add_page(
            "Stock", self.stock_view, "warehouse-svgrepo-com.svg"
        )  # Stock page

        # Add Settings Page - Placed at the bottom
        self.add_page(
            "Paramètres",
            self.settings_view,
            "settings-svgrepo-com.svg",  # Use a settings icon
        )

        # Set the default selected page in the navigation list to be the first one (Dashboard).
        self.nav_list.setCurrentRow(0)
        # Explicitly call change_page for the first page to ensure its data is loaded and displayed correctly on startup.
        self.change_page(0)

    def add_page(
        self, name, widget, icon_name=None
    ):  # Method to add a page (a view widget) to both the navigation list and the stacked widget.
        item = QListWidgetItem(
            name
        )  # Create a new list item with the given display name.
        # Set a preferred size hint for the item, especially its height, for consistent item appearance.
        # The height is taken from the FONTS theme variable or defaults to 55.
        item.setSizeHint(QSize(0, int(FONTS.get("sidebar_item_height", 55))))

        if icon_name:  # If an icon file name is provided:
            icon_path = os.path.join(
                ICON_DIR, icon_name
            )  # Construct the full, absolute path to the icon file.
            if os.path.exists(
                icon_path
            ):  # Check if the icon file actually exists at the path.
                item.setIcon(QIcon(icon_path))  # Set the icon for the list item.
            else:
                # Print a warning if the icon file is not found. This helps in debugging missing assets.
                print(f"Sidebar icon not found: {icon_path}")
                logger.warning(f"Sidebar icon not found: {icon_path}")

        self.nav_list.addItem(
            item
        )  # Add the newly created QListWidgetItem to the navigation QListWidget.
        self.stacked_widget.addWidget(
            widget
        )  # Add the corresponding view widget to the QStackedWidget. The order of addition matters for indexing.

    def change_page(
        self, index
    ):  # Method called when the selected item in the navigation list changes.
        # `index` is the row number of the selected item in QListWidget, which corresponds to the index in QStackedWidget.
        self.stacked_widget.setCurrentIndex(
            index
        )  # Change the visible page in the QStackedWidget.
        current_widget = self.stacked_widget.widget(
            index
        )  # Get a reference to the currently visible widget (the page).

        # --- Data Loading/Refreshing Logic for Different Views ---
        # When a page becomes active, it's often necessary to load or refresh its data.
        # This section checks if the current_widget has specific data loading methods and calls them.
        # This pattern ensures that views display up-to-date information.

        # Common method for general data refresh, e.g., Dashboard.
        if hasattr(current_widget, "load_data") and callable(
            getattr(current_widget, "load_data")
        ):
            current_widget.load_data()
        # Specific load methods for CustomerView.
        elif hasattr(current_widget, "load_customers") and callable(
            getattr(current_widget, "load_customers")
        ):
            current_widget.load_customers()
        # Specific load methods for ProductView.
        elif hasattr(current_widget, "load_products") and callable(
            getattr(current_widget, "load_products")
        ):
            current_widget.load_products()
            if hasattr(current_widget, "load_categories") and callable(
                getattr(current_widget, "load_categories")
            ):  # Product view might also need categories (e.g., for filters).
                current_widget.load_categories()
        # Specific load methods for PurchaseView.
        elif hasattr(current_widget, "load_purchase_history") and callable(
            getattr(current_widget, "load_purchase_history")
        ):
            current_widget.load_purchase_history()
            if hasattr(current_widget, "load_products_for_combo") and callable(
                getattr(current_widget, "load_products_for_combo")
            ):  # Purchase view needs product list for its combobox.
                current_widget.load_products_for_combo()
        # Specific load methods for SaleView.
        elif hasattr(current_widget, "load_sales_history") and callable(
            getattr(current_widget, "load_sales_history")
        ):
            current_widget.load_sales_history()
            if hasattr(current_widget, "load_products_for_sale") and callable(
                getattr(current_widget, "load_products_for_sale")
            ):  # Sale view needs products for its combobox.
                current_widget.load_products_for_sale()
            if hasattr(current_widget, "load_customers_for_sale") and callable(
                getattr(current_widget, "load_customers_for_sale")
            ):  # Sale view needs customers for its combobox.
                current_widget.load_customers_for_sale()
        # Specific load methods for StockView.
        elif hasattr(current_widget, "load_stock_data") and callable(
            getattr(current_widget, "load_stock_data")
        ):
            current_widget.load_stock_data()
            if hasattr(current_widget, "load_categories_filter") and callable(
                getattr(current_widget, "load_categories_filter")
            ):  # Stock view might have category filters.
                current_widget.load_categories_filter()
        # SettingsView doesn't typically need a load_data method unless it loads settings from a file/db.

        # A more generic refresh method that views could implement.
        # This can be a single entry point for data refresh if views adopt this method name.
        if hasattr(current_widget, "refresh_view_data") and callable(
            getattr(current_widget, "refresh_view_data")
        ):
            current_widget.refresh_view_data()

    def refresh_on_sale_purchase_product_change(self):
        """
        Called when a sale, purchase, or product update occurs.
        Refreshes data in multiple views that might be affected by these changes
        to ensure data consistency across the application.
        """
        print(
            "Refreshing views due to sale, purchase, or product update..."
        )  # Logging for debug.
        logger.info("Refreshing views due to sale, purchase, or product update...")

        # Refresh Dashboard: Likely shows summary data that depends on sales, products, stock.
        if hasattr(self.dashboard_view, "load_data") and callable(
            getattr(self.dashboard_view, "load_data")
        ):
            self.dashboard_view.load_data()

        # Refresh Product View:
        # - Product list itself might have changed (e.g., stock count if displayed, or if product details were edited).
        if hasattr(self.product_view, "load_products") and callable(
            getattr(self.product_view, "load_products")
        ):
            self.product_view.load_products()
        # - Categories might change if a product update involved a new category.
        if hasattr(self.product_view, "load_categories") and callable(
            getattr(self.product_view, "load_categories")
        ):
            self.product_view.load_categories()

        # Refresh Purchase View:
        # - The list of products available for purchase (in a combobox) needs to be up-to-date.
        if hasattr(self.purchase_view, "load_products_for_combo") and callable(
            getattr(self.purchase_view, "load_products_for_combo")
        ):
            self.purchase_view.load_products_for_combo()
        # - Purchase history itself should be current.
        if hasattr(self.purchase_view, "load_purchase_history") and callable(
            getattr(self.purchase_view, "load_purchase_history")
        ):
            self.purchase_view.load_purchase_history()

        # Refresh Stock View: Stock levels are directly affected by sales and purchases.
        if hasattr(self.stock_view, "load_stock_data") and callable(
            getattr(self.stock_view, "load_stock_data")
        ):
            self.stock_view.load_stock_data()
        # - Category filters in stock view might need updating.
        if hasattr(self.stock_view, "load_categories_filter") and callable(
            getattr(self.stock_view, "load_categories_filter")
        ):
            self.stock_view.load_categories_filter()

        # Refresh Sale View:
        # - The list of products available for sale (in a combobox) needs up-to-date stock and product info.
        if hasattr(self.sale_view, "load_products_for_sale") and callable(
            getattr(self.sale_view, "load_products_for_sale")
        ):
            self.sale_view.load_products_for_sale()
        # - Sales history should be current.
        if hasattr(self.sale_view, "load_sales_history") and callable(
            getattr(self.sale_view, "load_sales_history")
        ):
            self.sale_view.load_sales_history()
        # Note: Customer data refresh (e.g., for SaleView's customer combobox) is handled by `refresh_customer_related_views`.

    def refresh_customer_related_views(self):
        """
        Called when customer data is updated.
        Refreshes views that depend on customer information.
        """
        print("Refreshing customer-related views...")  # Logging for debug.
        logger.info("Refreshing customer-related views...")

        # Refresh Customer View: The main list of customers.
        if hasattr(self.customer_view, "load_customers") and callable(
            getattr(self.customer_view, "load_customers")
        ):
            self.customer_view.load_customers()

        # Refresh Sale View: The customer combobox in the SaleView needs to be up-to-date.
        if hasattr(self.sale_view, "load_customers_for_sale") and callable(
            getattr(self.sale_view, "load_customers_for_sale")
        ):
            self.sale_view.load_customers_for_sale()

        # Refresh Dashboard: Might show customer counts or other customer-related summaries.
        if hasattr(self.dashboard_view, "load_data") and callable(
            getattr(self.dashboard_view, "load_data")
        ):  # Check if callable
            self.dashboard_view.load_data()

    # Example data preparation function, might be part of a view (e.g., DashboardView)
    # that displays graphs.
    def prepare_graph_data(self, raw_data):
        """
        Ensures all data points for a graph are non-negative.
        This is a simple data cleaning step before plotting.
        Args:
            raw_data (list): A list of numerical values.
        Returns:
            list: A new list where all negative values are replaced with 0.
        """
        # Clamp all values to be >= 0. This prevents issues with graph libraries
        # that might not handle negative values appropriately for certain chart types (e.g., bar charts of counts).
        return [max(0, value) for value in raw_data]

    # Example usage comment (how this function might be used before plotting):
    # graph_data = self.prepare_graph_data(raw_data_from_database)
    # plot_library.plot(graph_data)


# This block executes if the script is run directly (e.g., `python main.py`).
# It's the main entry point of the application.
if __name__ == "__main__":
    # --- Database Initialization Check ---
    # Determine the directory where the script is located.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the SQLite database file.
    # It's assumed to be in the same directory as main.py or a known relative path.
    db_file_path = os.path.join(script_dir, "gestion_commerciale.db")

    # --- Logging Setup (if not already configured elsewhere globally) ---
    # This basic config is often done once. If error_handler.py does it, this might be redundant or could conflict.
    # For simplicity, ensure logger is available.
    if not logging.getLogger(
        "inventory_app"
    ).hasHandlers():  # Check if handlers are already set
        log_dir_main = os.path.join(script_dir, "logs")
        os.makedirs(log_dir_main, exist_ok=True)
        log_file_main = os.path.join(
            log_dir_main, "app_main_errors.log"
        )  # Separate log for main if desired
        logging.basicConfig(
            level=logging.INFO,  # Set to INFO or DEBUG for more verbose startup logs
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file_main),
                logging.StreamHandler(sys.stdout),  # Also log to console
            ],
        )
    logger.info(f"Application starting. Database path: {db_file_path}")

    # Check if the database file exists.
    if not os.path.exists(db_file_path):
        # If the database file does not exist, print a message and initialize it.
        print("Database file not found. Initializing...")
        logger.info("Database file not found. Initializing...")
        initialize_database()  # Call the function to create tables and triggers.
    else:
        # If the database file exists, print a confirmation message.
        print("Database file found.")
        logger.info("Database file found.")

    # --- Application Setup ---
    # Create the QApplication instance. `sys.argv` allows passing command-line arguments to the application.
    app = QApplication(sys.argv)
    # Apply global styles to the application instance. This ensures a consistent theme.
    apply_global_style(app)

    # --- Main Window Creation and Display ---
    # Create an instance of the MainWindow class.
    window = MainWindow()
    # Show the main window.
    window.show()

    # --- Application Execution ---
    # Start the Qt event loop. `app.exec()` blocks until the application exits.
    # `sys.exit()` ensures that the application's exit code is returned to the operating system.
    sys.exit(app.exec())
