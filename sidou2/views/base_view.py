# Updated content for sidou2/views/base_view.py
# Import necessary Qt modules for creating graphical user interfaces
from PyQt6.QtWidgets import (
    QWidget,  # Base class for all user interface objects
    QVBoxLayout,  # Lines up widgets vertically
    QHBoxLayout,  # Lines up widgets horizontally
    QLabel,  # For displaying text or images
    QPushButton,  # Command button
    QTableWidget,  # Table display
    QTableWidgetItem,  # Item for use in QTableWidget
    QMessageBox,  # Dialog for showing messages
    QHeaderView,  # Header for tables and trees
    QAbstractItemView,  # Abstract model for item views
    QGridLayout,  # Layout that arranges widgets in a grid
    QComboBox,  # Dropdown list
    QLineEdit,  # Single-line text input
    QSpinBox,  # Integer spin box
    QDoubleSpinBox,  # Double precision spin box
    QTextEdit,  # Multi-line text input
)
from PyQt6.QtCore import Qt, pyqtSignal  # Core Qt functionalities, including signals

# Import theme settings (colors, fonts, spacing, radius) from a local 'theme.py' file
from theme import COLORS, FONTS, SPACING, RADIUS, STYLES  # Added STYLES


class BaseView(QWidget):  # Define a class named BaseView that inherits from QWidget
    """
    Base class for all view components in the application.
    It provides common functionalities like creating titles, tables, buttons,
    and showing messages to reduce code duplication across different views.
    This is particularly useful for a group project to ensure consistency.
    """

    # Define a signal that can be emitted when data in the view is updated.
    # Other parts of the application can connect to this signal.
    data_updated = pyqtSignal()

    def __init__(self, title=""):  # Constructor for the BaseView class
        """
        Initializes the BaseView.
        Args:
            title (str): The default title for the view.
        """
        super().__init__()  # Call the constructor of the parent class (QWidget)
        self.title = title  # Store the provided title
        # Create a vertical box layout as the main layout for this widget
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)  # Apply this layout to the widget
        # Apply main window style from theme to the BaseView (acts as a page background)
        # This ensures that all views inheriting from BaseView will have a consistent background style.
        self.setStyleSheet(STYLES.get("main_window", ""))

    def create_title(self, title=None):
        """
        Creates and adds a standardized title label to the main layout.
        This helps maintain a consistent look and feel for titles across views.
        Using this method in all views ensures that titles are styled uniformly
        according to the theme, which is important for a polished group project presentation.

        Args:
            title (str, optional): The text for the title. If None, uses self.title.
                                   This allows views to either use a default title
                                   or specify a custom one.
        Returns:
            QLabel: The created title label widget.
        """
        if (
            title is None
        ):  # If no specific title is provided, use the instance's default title
            title = self.title

        title_label = QLabel(title)  # Create a QLabel widget for the title
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center-align the title text
        # Apply styling to the title label using f-strings to incorporate theme values.
        # It fetches the 'title' style definition from the STYLES dictionary in 'theme.py'.
        # If the 'title' key is not found, it falls back to an inline defined style.
        # This centralization of style definitions in 'theme.py' is crucial for group projects
        # as it allows for easy theme changes without modifying individual view files.
        title_label.setStyleSheet(
            STYLES.get(
                "title",  # Fallback inline style
                f"font-size: {FONTS['heading']}pt; "
                f"font-weight: bold; "
                f"margin: {SPACING['lg']} 0 {SPACING['xl']} 0; "  # Added more bottom margin
                f"color: {COLORS['text_primary']};",
            )
        )
        self.main_layout.addWidget(
            title_label
        )  # Add the title label to the main layout
        return title_label  # Return the created label

    def create_table(
        self,
        columns,
        hide_vertical_header=True,
        selection_behavior="rows",
        selection_mode="single",
    ):
        """
        Creates and returns a QTableWidget with specified columns and properties.
        This provides a consistent setup for tables used in different views.
        Standardizing table creation helps in maintaining a uniform data presentation
        style across the application, which is beneficial for a group project's coherence.

        Args:
            columns (list): A list of strings for the table header labels.
            hide_vertical_header (bool): If True, the vertical header (row numbers) is hidden.
                                         Defaults to True for a cleaner look.
            selection_behavior (str): "rows" or "items" for selection behavior.
                                      "rows" (default) is often more user-friendly.
            selection_mode (str): "single", "multi", or "none" for selection mode.
                                  "single" (default) allows only one row/item to be selected.
        Returns:
            QTableWidget: The configured table widget.
        """
        table = QTableWidget()  # Create a QTableWidget instance
        table.setColumnCount(len(columns))  # Set the number of columns
        table.setHorizontalHeaderLabels(
            columns
        )  # Set the labels for the horizontal header

        # Apply table style from theme.py. This ensures all tables have a consistent look.
        table.setStyleSheet(STYLES.get("table", ""))

        # Configure how items are selected in the table
        if selection_behavior == "rows":
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        elif selection_behavior == "items":
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

        # Configure whether single or multiple items can be selected
        if selection_mode == "single":
            table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        elif selection_mode == "multi":
            table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        elif selection_mode == "none":
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        # Disable editing of table items directly in the table.
        # Data modification should typically go through forms or dedicated dialogs.
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Hide or show the vertical header (row numbers)
        table.verticalHeader().setVisible(not hide_vertical_header)
        # Set how columns are resized.
        # 'Interactive' allows users to resize columns manually.
        # 'StretchLastSection' ensures the last column stretches to fill remaining space.
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        table.horizontalHeader().setStretchLastSection(True)

        return table  # Return the created table

    def create_button_layout(self):
        """
        Creates and returns a QHBoxLayout, typically used for arranging buttons.
        This promotes a consistent horizontal arrangement and spacing for button groups.

        Returns:
            QHBoxLayout: An empty horizontal box layout, styled with spacing from the theme.
        """
        button_layout = QHBoxLayout()  # Create a horizontal box layout
        # Add spacing from theme.py, converting the string 'px' value to an integer.
        button_layout.setSpacing(int(SPACING.get("md", "12px").replace("px", "")))
        return button_layout  # Return the layout

    def create_button(
        self,
        text,
        callback=None,
        enabled=True,
        tooltip=None,
        style_key="button_primary",
    ):
        """
        Creates and returns a QPushButton with specified text and properties.
        Applies a style from the theme based on style_key. This is essential for
        maintaining visual consistency of buttons (e.g., primary, secondary, destructive actions)
        across the application, a key point for group projects.

        Args:
            text (str): The text to display on the button.
            callback (function, optional): Function to call when the button is clicked.
            enabled (bool): If True, the button is enabled; otherwise, disabled. Defaults to True.
            tooltip (str, optional): Text to display as a tooltip for the button.
            style_key (str): Key for STYLES dictionary in theme.py (e.g., "button_primary",
                               "button_secondary", "button_destructive"). Defaults to "button_primary".
        Returns:
            QPushButton: The configured button widget.
        """
        button = QPushButton(text)  # Create a QPushButton with the given text
        if callback:  # If a callback function is provided
            button.clicked.connect(
                callback
            )  # Connect the button's clicked signal to the callback
        button.setEnabled(enabled)  # Set the button's enabled state
        if tooltip:  # If tooltip text is provided
            button.setToolTip(tooltip)  # Set the tooltip for the button

        # Apply button style from theme.py using the provided style_key.
        # This allows for different button appearances (primary, secondary, etc.)
        # while keeping the styling definitions centralized.
        button.setStyleSheet(STYLES.get(style_key, ""))
        # Example of ensuring minimum height if not set by the theme stylesheet directly for that key.
        # Many button styles in theme.py already set min-height.
        # if "min-height" not in STYLES.get(style_key, ""):
        #     button.setMinimumHeight(40) # Or use a theme variable like int(FONTS.get("button_min_height", "40px").replace("px",""))

        return button  # Return the created button

    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        """
        Displays a message box with a given title, message, and icon.
        This is a generic way to show feedback to the user (e.g., success messages, errors, warnings).
        Using a common method for messages ensures they all look and behave similarly.

        Args:
            title (str): The title of the message box window.
            message (str): The message to display.
            icon (QMessageBox.Icon): The icon to show (Information, Warning, Critical, etc.).
                                     Defaults to QMessageBox.Icon.Information.
        """
        msg_box = QMessageBox(
            self
        )  # Create a QMessageBox instance, parented to this view
        msg_box.setWindowTitle(title)  # Set the window title
        msg_box.setText(message)  # Set the main message text
        msg_box.setIcon(icon)  # Set the icon for the message box
        # Optional: Apply global styling to QMessageBox if needed, though it usually picks up system theme.
        # msg_box.setStyleSheet(f"background-color: {COLORS['surface']}; color: {COLORS['text_primary']};")
        msg_box.exec()  # Show the message box and wait for user interaction

    def show_error(self, title, message):
        """Helper method to display an error message box using the critical icon.
        Simplifies showing error messages from various parts of the application.
        """
        self.show_message(title, message, QMessageBox.Icon.Critical)

    def show_warning(self, title, message):
        """Helper method to display a warning message box using the warning icon.
        Simplifies showing warning messages.
        """
        self.show_message(title, message, QMessageBox.Icon.Warning)

    def show_info(self, title, message):
        """Helper method to display an informational message box using the information icon.
        Simplifies showing informational messages.
        """
        self.show_message(title, message, QMessageBox.Icon.Information)

    def show_confirmation(
        self,
        title,
        message,
        icon=QMessageBox.Icon.Question,
        buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        default_button=QMessageBox.StandardButton.No,
    ):
        """
        Displays a confirmation message box with specified title, message, icon, and buttons.
        Returns True if the user confirms (clicks Yes), False otherwise.

        Args:
            title (str): The title of the confirmation dialog.
            message (str): The confirmation message/question.
            icon (QMessageBox.Icon): The icon to display. Defaults to Question.
            buttons (QMessageBox.StandardButtons): Buttons to display. Defaults to Yes|No.
            default_button (QMessageBox.StandardButton): The default selected button.
        Returns:
            bool: True if the user confirms (clicks Yes), False otherwise.
        """
        reply = QMessageBox.question(
            self,  # Parent widget
            title,  # Window title
            message,  # Message text
            buttons,  # Button options
            default_button,  # Default button
        )
        if buttons == (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No):
            return reply == QMessageBox.StandardButton.Yes
        return reply

    def show_message_custom(
        self,
        title,
        message,
        icon=QMessageBox.Icon.Information,
        buttons=QMessageBox.StandardButton.Ok,
        default_button=None,
    ):
        """
        Displays a customizable message box with specified icon and buttons.
        Returns the button that was clicked.

        Args:
            title (str): The title of the message box.
            message (str): The message to display.
            icon (QMessageBox.Icon): The icon to show.
            buttons (QMessageBox.StandardButtons): Buttons to display.
            default_button (QMessageBox.StandardButton): The default selected button.
        Returns:
            QMessageBox.StandardButton: The button that was clicked.
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(buttons)
        if default_button:
            msg_box.setDefaultButton(default_button)
        return msg_box.exec()

    def create_search_filter_layout(
        self, search_placeholder="Rechercher...", with_category_filter=False
    ):
        """
        Creates a layout containing a search input field and optionally a category filter.
        This is useful for views that need to filter displayed data (e.g., product lists, customer lists).
        Provides a consistent UI for search/filter functionality.

        Args:
            search_placeholder (str): Placeholder text for the search input.
            with_category_filter (bool): If True, adds a QComboBox for category filtering.
                                         Defaults to False.
        Returns:
            tuple: (QLineEdit, QComboBox or None) - The search input and category combo box (if created).
        """
        search_filter_layout = QHBoxLayout()  # Create a horizontal layout
        search_filter_layout.setSpacing(
            int(SPACING.get("md", "12px").replace("px", ""))
        )
        # Define content margins for the search/filter layout itself
        search_filter_layout.setContentsMargins(
            0,  # left
            int(SPACING.get("sm", "8px").replace("px", "")),  # top
            0,  # right
            int(
                SPACING.get("lg", "16px").replace("px", "")
            ),  # bottom (more space before the main content like a table)
        )

        search_label = QLabel("Rechercher:")  # Label for the search input
        # Apply a secondary label style from theme for less emphasis than primary labels.
        search_label.setStyleSheet(
            STYLES.get("label_secondary", f"color: {COLORS['text_secondary']};")
        )

        search_input = QLineEdit()  # Create the search input field
        search_input.setPlaceholderText(search_placeholder)  # Set placeholder text
        search_input.setStyleSheet(
            STYLES.get("input", "")
        )  # Apply input style from theme

        search_filter_layout.addWidget(search_label)  # Add label to layout
        search_filter_layout.addWidget(search_input)  # Add input field to layout
        search_filter_layout.addStretch(
            1
        )  # Add stretch to push category filter (if any) to the right or fill space

        category_filter_combo = None  # Initialize category filter as None
        if with_category_filter:  # If category filter is requested
            category_label = QLabel("Catégorie:")  # Label for category filter
            category_label.setStyleSheet(
                STYLES.get("label_secondary", f"color: {COLORS['text_secondary']};")
            )

            category_filter_combo = QComboBox()  # Create a QComboBox for categories
            category_filter_combo.addItem("Toutes les catégories")  # Default item
            category_filter_combo.setStyleSheet(
                STYLES.get("input", "")
            )  # Apply input style (same as other inputs for consistency)
            category_filter_combo.setMinimumWidth(150)  # Ensure it has enough width

            search_filter_layout.addWidget(category_label)  # Add label to layout
            search_filter_layout.addWidget(
                category_filter_combo
            )  # Add combo box to layout

        self.main_layout.addLayout(
            search_filter_layout
        )  # Add this sub-layout to the main view layout
        return search_input, category_filter_combo  # Return the created widgets

    def create_form_widget(self):
        """
        Creates a styled QWidget to act as a container for form elements,
        with a QGridLayout. Uses "card" or "group_box" style from theme for the container.
        This helps in visually grouping form fields and applying consistent styling.
        A QGridLayout is suitable for arranging labels and inputs in a form.

        Returns:
            tuple: (QWidget, QGridLayout) - The form container widget and its layout.
        """
        form_widget = (
            QWidget()
        )  # Create a base QWidget that will act as the form container
        # Apply a style to this container, typically a "card" or "group_box" style from the theme
        # to give it a distinct background and border, separating it visually.
        form_widget.setStyleSheet(
            STYLES.get(
                "card", STYLES.get("group_box", "")
            )  # Prefer "card" style, fallback to "group_box"
        )

        form_layout = QGridLayout(
            form_widget
        )  # Create a QGridLayout and set it on the form_widget
        form_layout.setSpacing(
            int(SPACING["md"].replace("px", ""))
        )  # Spacing between cells in the grid
        # Content margins define the padding inside the form_widget, around the grid layout.
        form_layout.setContentsMargins(
            int(SPACING["lg"].replace("px", "")),  # Left margin
            int(SPACING["lg"].replace("px", "")),  # Top margin
            int(SPACING["lg"].replace("px", "")),  # Right margin
            int(SPACING["lg"].replace("px", "")),  # Bottom margin
        )
        return form_widget, form_layout

    def create_crud_buttons(
        self,
        add_handler=None,
        update_handler=None,
        delete_handler=None,
        clear_handler=None,
    ):
        """
        Creates a standard set of CRUD (Create, Read, Update, Delete) action buttons
        and a clear button, arranged in a horizontal layout.
        This standardizes the layout and styling of common form actions.
        'Update' and 'Delete' buttons are initially disabled, assuming they require a selection.

        Args:
            add_handler (function, optional): Callback for the 'Add' button.
            update_handler (function, optional): Callback for the 'Update' button.
            delete_handler (function, optional): Callback for the 'Delete' button.
            clear_handler (function, optional): Callback for the 'Clear Form' button.
        Returns:
            tuple: (QPushButton or None, ...) for add, update, delete, clear buttons,
                   allowing individual views to store references to these buttons if needed
                   (e.g., to enable/disable them based on context).
        """
        button_layout = (
            self.create_button_layout()
        )  # Get a themed horizontal button layout

        add_button = None
        if add_handler:
            # Create an "Add" button with primary styling.
            add_button = self.create_button(
                "Ajouter", add_handler, style_key="button_primary"
            )
            button_layout.addWidget(add_button)

        update_button = None
        if update_handler:
            # Create an "Update" button with secondary styling, initially disabled.
            update_button = self.create_button(
                "Modifier", update_handler, enabled=False, style_key="button_secondary"
            )
            button_layout.addWidget(update_button)

        delete_button = None
        if delete_handler:
            # Create a "Delete" button with destructive styling, initially disabled.
            delete_button = self.create_button(
                "Supprimer",
                delete_handler,
                enabled=False,
                style_key="button_destructive",
            )
            button_layout.addWidget(delete_button)

        button_layout.addStretch()  # Add stretchable space to push the "Clear" button to the right

        clear_button = None
        if clear_handler:
            # Create a "Clear Form" button with ghost styling (less prominent).
            clear_button = self.create_button(
                "Effacer Formulaire", clear_handler, style_key="button_ghost"
            )
            button_layout.addWidget(clear_button)

        self.main_layout.addLayout(
            button_layout
        )  # Add the button layout to the main view layout
        return add_button, update_button, delete_button, clear_button

    def apply_input_styles(self, widgets):
        """
        Applies the 'input' style from theme.py to a list of widgets.
        This centralizes input field styling, ensuring all inputs (QLineEdit, QComboBox, etc.)
        have a consistent appearance based on the theme.

        Args:
            widgets (list): A list of QLineEdit, QComboBox, QSpinBox, QTextEdit, etc.
        """
        input_style = STYLES.get(
            "input", ""
        )  # Get the general 'input' style from the theme
        for widget in widgets:
            if widget:  # Check if widget is not None
                widget.setStyleSheet(input_style)
                # For certain input types, a minimum height might be desirable if not already
                # defined in the stylesheet for 'input'. This improves usability.
                if isinstance(widget, (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)):
                    # Check if 'min-height' is already part of the applied style string
                    if "min-height" not in input_style:
                        widget.setMinimumHeight(
                            35
                        )  # Default minimum height for single-line inputs
                elif isinstance(widget, QTextEdit):
                    # QTextEdit (multi-line) might need a larger default minimum height
                    if "min-height" not in input_style:
                        widget.setMinimumHeight(70)

    def apply_label_styles(self, labels, style_key="label"):
        """
        Applies a label style from theme.py to a list of QLabels.
        Allows for consistent styling of labels (e.g., primary, secondary, bold).

        Args:
            labels (list): A list of QLabel widgets.
            style_key (str): Key for STYLES dictionary in theme.py (e.g., "label",
                               "label_secondary", "label_bold"). Defaults to "label".
        """
        label_style = STYLES.get(
            style_key, ""
        )  # Get the specified label style from the theme
        for label in labels:
            if label:  # Check if label is not None
                label.setStyleSheet(label_style)

    def populate_category_combo(
        self, combo_box, categories=None, default_text="Toutes les catégories"
    ):
        """
        Populates a QComboBox with categories, adding a default 'All Categories' item.
        This is a common task for views that filter by category (e.g., ProductView, StockView).
        It tries to preserve the currently selected item if it exists in the new list.

        Args:
            combo_box (QComboBox): The combo box to populate.
            categories (list, optional): List of category strings. If None, it attempts to
                                         import and call `get_all_categories()` from the database module.
                                         This dynamic loading is useful but creates a dependency.
            default_text (str): The text for the default item (e.g., "All Categories").
        """
        current_text = (
            combo_box.currentText()
        )  # Store the current selection before clearing
        combo_box.blockSignals(
            True
        )  # Block signals to prevent unwanted events during repopulation
        combo_box.clear()  # Remove all existing items
        combo_box.addItem(default_text)  # Add the default "all categories" item

        if categories is None:  # If no categories list is provided externally
            try:
                # Attempt to dynamically import and fetch categories from the database.
                # This is convenient but makes BaseView dependent on the database module structure.
                # For a very strict separation of concerns, categories might be passed in.
                from database.database import get_all_categories

                categories = get_all_categories()
            except Exception:  # Catch potential import errors or database errors
                categories = []  # Default to an empty list on failure

        if categories:  # If categories were fetched or provided
            combo_box.addItems(categories)  # Add them to the combo box
            # Try to restore the previous selection
            index = combo_box.findText(current_text)
            if index != -1:  # If the previous text is found in the new list
                combo_box.setCurrentIndex(index)  # Reselect it
            else:
                combo_box.setCurrentIndex(0)  # Otherwise, select the default item
        combo_box.blockSignals(False)  # Re-enable signals
