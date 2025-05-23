# Updated content for sidou2/views/dashboard_view.py
import os  # Standard library for interacting with the operating system, e.g., for path manipulation.
import sys  # Standard library for system-specific parameters and functions, e.g., for running the app.
import datetime  # Standard library for working with dates and times.
from PyQt6.QtWidgets import (  # Import necessary UI components from PyQt6.
    QApplication,  # Manages the application's control flow and main settings.
    QWidget,  # Base class for all UI objects.
    QVBoxLayout,  # Arranges widgets vertically.
    QLabel,  # Displays text or images.
    QGridLayout,  # Arranges widgets in a grid.
    QFrame,  # Provides a frame, often used as a container or for styling.
    QHBoxLayout,  # Arranges widgets horizontally.
    QGraphicsDropShadowEffect,  # Provides a drop shadow effect for widgets.
    QSizePolicy,  # Describes how a widget should resize.
)
from PyQt6.QtCore import Qt, pyqtProperty  # Import core Qt functionalities.
from PyQt6.QtGui import (  # Import classes for graphical elements.
    QFont,  # For specifying text fonts.
    QColor,  # For specifying colors.
    QPalette,  # Manages the color scheme of widgets.
    QLinearGradient,  # For creating linear gradient brushes.
    QGradient,  # Base class for gradient brushes.
    QBrush,  # For filling shapes with patterns or colors.
)

# Ensure all necessary theme components are imported. These are custom modules for styling.
from theme import (
    COLORS as theme_COLORS,  # Dictionary of color definitions.
    DASHBOARD_COLORS,  # Specific colors for dashboard elements.
    CHART_COLORS,  # Colors for charts.
    STYLES as theme_STYLES,  # Dictionary of stylesheet strings.
    FONTS as theme_FONTS,  # Dictionary of font definitions.
    SPACING,  # Dictionary for padding and margin values.
    RADIUS,  # Dictionary for border-radius values.
)

try:
    # Attempt to import pyqtgraph for plotting charts.
    import pyqtgraph as pg
    from pyqtgraph import (
        DateAxisItem,
        BarGraphItem,
    )  # Specific items for date-based axes and bar graphs.

    PYQTGRAPH_AVAILABLE = (
        True  # Flag to indicate if pyqtgraph is successfully imported.
    )
except ImportError:
    PYQTGRAPH_AVAILABLE = False  # Flag if pyqtgraph is not found.
    print(
        "Warning: pyqtgraph not found. Graphs will not be displayed on the dashboard."
    )

# Import database interaction functions.
from database.database import (
    get_db_connection,  # Function to establish a database connection.
    get_monthly_sales_trend,  # Function to fetch data for sales trend chart.
    get_top_selling_products,  # Function to fetch data for top products chart.
)


class DashboardView(
    QWidget
):  # Main class for the dashboard view, inheriting from QWidget.
    def __init__(self):  # Constructor for the DashboardView.
        super().__init__()  # Call the constructor of the parent class (QWidget).

        # Set the background and text colors for the dashboard using the application's palette.
        palette = self.palette()
        palette.setColor(
            QPalette.ColorRole.Window,  # Role for the widget's background.
            QColor(
                theme_COLORS.get("background_dark", "#1e293b")
            ),  # Dark background color from theme.
        )
        palette.setColor(
            QPalette.ColorRole.WindowText,  # Role for the widget's foreground (text).
            QColor(
                theme_COLORS.get("text_light", "#f8fafc")
            ),  # Light text color from theme.
        )
        self.setAutoFillBackground(
            True
        )  # Ensure the background is filled automatically.
        self.setPalette(palette)  # Apply the configured palette.

        self.init_ui()  # Initialize the user interface elements.
        self.load_data()  # Load the data to be displayed on the dashboard.

    def init_ui(self):  # Method to set up the user interface of the dashboard.
        main_layout = QVBoxLayout(
            self
        )  # Create a vertical layout for the main dashboard area.
        # Set content margins using spacing values from the theme.
        main_layout.setContentsMargins(
            int(SPACING.get("xl", "20px").replace("px", "")),
            int(SPACING.get("xl", "20px").replace("px", "")),
            int(SPACING.get("xl", "20px").replace("px", "")),
            int(SPACING.get("xl", "20px").replace("px", "")),
        )
        main_layout.setSpacing(
            int(SPACING.get("2xl", "25px").replace("px", ""))
        )  # Set spacing between widgets.
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align content to the top.

        # Create and style the main title label for the dashboard.
        title_label = QLabel("Tableau de Bord")
        title_font = QFont(
            theme_FONTS.get("font_family", "Arial"),
            int(theme_FONTS.get("display", 24)),  # Font family and size from theme.
        )
        title_font.setBold(True)  # Make title bold.
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align title to the left.
        title_label.setStyleSheet(
            f"color: {theme_COLORS.get('text_light', '#000000')}; margin-bottom: {SPACING.get('md','10px')};"  # Style from theme.
        )
        main_layout.addWidget(title_label)  # Add title to the layout.

        # Create a grid layout for summary cards (KPIs).
        summary_grid = QGridLayout()
        summary_grid.setSpacing(
            int(SPACING.get("xl", "20px").replace("px", ""))
        )  # Spacing for the grid.
        main_layout.addLayout(summary_grid)  # Add grid to the main layout.

        # Create summary cards for key metrics using a helper function.
        # Each card displays a title, a value (initially "0" or "0.00 DA"), and has a specific background color.
        self.total_clients_card = self._create_summary_card(
            "Clients Actifs",  # Title of the card
            "0",  # Initial value displayed
            DASHBOARD_COLORS.get(
                "clients", "#3498DB"
            ),  # Background color for this specific card, defined in theme.DASHBOARD_COLORS
        )
        self.total_products_card = self._create_summary_card(
            "Produits Référencés", "0", DASHBOARD_COLORS.get("products", "#2ECC71")
        )
        self.total_sales_card = self._create_summary_card(
            "Ventes (Mois Actuel)",
            "0.00 DA",  # "DA" likely refers to Algerian Dinar, the local currency.
            DASHBOARD_COLORS.get("sales", "#E74C3C"),
        )
        self.low_stock_card = self._create_summary_card(
            "Stock Faible (<5)",  # Indicates products with stock quantity less than 5.
            "0",
            DASHBOARD_COLORS.get("low_stock", "#F39C12"),
        )

        # Add summary cards to the grid layout at specified positions (row, column).
        summary_grid.addWidget(self.total_clients_card, 0, 0)  # Row 0, Column 0.
        summary_grid.addWidget(self.total_products_card, 0, 1)  # Row 0, Column 1.
        summary_grid.addWidget(self.total_sales_card, 1, 0)  # Row 1, Column 0.
        summary_grid.addWidget(self.low_stock_card, 1, 1)  # Row 1, Column 1.

        # Check if the pyqtgraph library is available for displaying charts.
        if PYQTGRAPH_AVAILABLE:
            charts_layout = (
                QHBoxLayout()
            )  # Create a horizontal layout to hold the charts.
            charts_layout.setSpacing(
                int(SPACING.get("xl", "20px").replace("px", ""))
            )  # Set spacing between charts.
            main_layout.addLayout(
                charts_layout
            )  # Add the chart layout to the main dashboard layout.

            # Create a frame for the sales trend chart using a helper function.
            # This frame will contain the chart title and the plot widget.
            self.sales_trend_plot_widget = self._create_chart_widget_frame(
                "Tendance des Ventes (12 Mois)"  # Title for the sales trend chart.
            )
            charts_layout.addWidget(
                self.sales_trend_plot_widget  # Add the sales trend chart frame to the charts layout.
            )

            # Create a frame for the top selling products chart.
            self.top_products_plot_widget = self._create_chart_widget_frame(
                "Top 5 Produits Vendus (Quantité)"  # Title for the top products chart.
            )
            charts_layout.addWidget(
                self.top_products_plot_widget  # Add the top products chart frame to the charts layout.
            )
        else:
            # If pyqtgraph is not available, display a warning message to the user.
            no_graph_label = QLabel(
                "Bibliothèque 'pyqtgraph' non installée. Graphiques désactivés."
            )
            no_graph_label.setStyleSheet(
                f"color: {theme_COLORS.get('warning', 'yellow')}; font-style: italic; font-size: {theme_FONTS.get('body_small',10)}pt; padding: {SPACING.get('lg','15px')};"  # Style the warning message using theme colors and fonts.
            )
            no_graph_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter  # Center the warning message.
            )
            main_layout.addWidget(
                no_graph_label
            )  # Add the warning message to the main layout.

        self.setLayout(
            main_layout
        )  # Apply the main layout to the DashboardView widget, arranging all UI elements.

    # Helper function to create a styled summary card (QFrame).
    # Parameters:
    #   title_text (str): The title to display on the card (e.g., "Clients Actifs").
    #   value_text (str): The initial value to display (e.g., "0"). This will be updated by load_data().
    #   bg_color_hex (str): The background color for the card in hexadecimal format.
    def _create_summary_card(self, title_text, value_text, bg_color_hex):
        card = QFrame()  # Create a QFrame, which will serve as the card container.
        card.setObjectName(
            "summaryCard"  # Set an object name for specific styling via QSS (Qt Style Sheets).
        )
        card.setFrameShape(
            QFrame.Shape.StyledPanel
        )  # Define the visual appearance of the frame's border.
        card.setFrameShadow(
            QFrame.Shadow.Raised  # Add a shadow effect to make the card appear raised.
        )
        card.setMinimumSize(200, 120)  # Set the minimum width and height for the card.
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,  # Allow the card to expand horizontally but keep a fixed vertical size.
        )

        # Apply a stylesheet to the card for custom styling.
        # Uses a linear gradient for the background color, blending from a lighter shade to the specified bg_color_hex.
        card.setStyleSheet(
            f"""
            QFrame#summaryCard {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {QColor(bg_color_hex).lighter(120).name()}, stop:1 {bg_color_hex});
                border-radius: {RADIUS.get('lg', '12px')}; /* Rounded corners, value from theme.RADIUS */
                padding: {SPACING.get('lg', '15px')}; /* Padding inside the card, value from theme.SPACING */
                color: {theme_COLORS.get('white', '#ffffff')}; /* Text color for the card, from theme.COLORS */
            }}
        """
        )

        # Apply a drop shadow effect for a more modern UI look.
        shadow = QGraphicsDropShadowEffect(self)  # Create the shadow effect.
        shadow.setBlurRadius(15)  # Set the blurriness of the shadow.
        shadow.setColor(
            QColor(0, 0, 0, 70)  # Set the shadow color (black with some transparency).
        )
        shadow.setOffset(2, 2)  # Set the horizontal and vertical offset of the shadow.
        card.setGraphicsEffect(shadow)  # Apply the shadow effect to the card.

        # Create a vertical layout for the content (title and value) within the card.
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(
            int(
                SPACING.get("sm", "8px").replace("px", "")
            )  # Spacing between title and value.
        )
        card_layout.setContentsMargins(
            0,
            0,
            0,
            0,  # No internal margins for the card_layout itself, padding is handled by the card's QSS.
        )

        # Create and style the title label for the card.
        title_label = QLabel(title_text)
        title_font = QFont(
            theme_FONTS.get("font_family", "Arial"),  # Font family from theme.FONTS.
            int(
                theme_FONTS.get("card_title_size", 11)
            ),  # Font size for card titles from theme.FONTS.
        )
        title_label.setFont(title_font)
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop  # Align title to the top-left.
        )
        title_label.setStyleSheet(
            f"color: {QColor(theme_COLORS.get('white', '#ffffff')).lighter(130).name()}; border: none; background: transparent;"  # Lighter text color for title, no border, transparent background.
        )

        # Create and style the value label for the card.
        value_label = QLabel(str(value_text))  # Display the metric's value.
        value_font = QFont(
            theme_FONTS.get("font_family", "Arial"),
            int(
                theme_FONTS.get("card_value_size", 20)
            ),  # Larger font size for the value from theme.FONTS.
        )
        value_font.setBold(True)  # Make the value text bold.
        value_label.setFont(value_font)
        value_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignBottom  # Align value to the bottom-left.
        )
        value_label.setObjectName(
            "valueLabel"
        )  # Set object name for potential specific styling.
        value_label.setStyleSheet(
            f"color: {theme_COLORS.get('white', '#ffffff')}; border: none; background: transparent;"  # Text color, no border, transparent background.
        )

        # Add title and value labels to the card's layout.
        card_layout.addWidget(title_label)
        card_layout.addStretch()  # Add stretchable space to push the value_label towards the bottom.
        card_layout.addWidget(value_label)

        card.value_label = (
            value_label  # Store a reference to the value label within the card object itself.
            # This allows easy access to update the card's value later (e.g., in load_data()).
        )
        return card  # Return the fully created and styled summary card widget.

    # Helper function to create a styled QFrame that will act as a container for a chart.
    # Parameters:
    #   title_text (str): The title to display above the chart within this frame.
    def _create_chart_widget_frame(self, title_text):
        chart_container_frame = (
            QFrame()
        )  # Create a QFrame to hold the chart and its title.
        chart_container_frame.setObjectName(
            "chartContainerFrame"  # Set an object name for specific styling via QSS.
        )
        chart_container_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )  # Define the frame's visual style.
        # Apply stylesheet for the chart container.
        # This sets the background color, border radius, and padding for the frame.
        chart_container_frame.setStyleSheet(
            f"""
            QFrame#chartContainerFrame {{
                background-color: {theme_COLORS.get('background_medium', '#334155')}; /* Medium dark background from theme. */
                border-radius: {RADIUS.get('lg', '12px')}; /* Rounded corners from theme. */
                padding: {SPACING.get('md', '10px')}; /* Padding inside the frame from theme. */
            }}
        """
        )
        chart_container_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,  # Allow the frame to expand both horizontally and vertically to fill available space.
        )

        # Create a vertical layout for the content (title and plot widget) within the chart container.
        container_layout = QVBoxLayout(chart_container_frame)
        container_layout.setContentsMargins(
            5, 5, 5, 5
        )  # Set small margins around the content.
        container_layout.setSpacing(
            int(
                SPACING.get("sm", "8px").replace("px", "")
            )  # Spacing between the title and the chart.
        )

        # Create and style the title label for the chart.
        title_label = QLabel(title_text)
        title_font = QFont(
            theme_FONTS.get("font_family", "Arial"),
            int(
                theme_FONTS.get("chart_widget_title_size", 12)
            ),  # Font size for chart titles from theme.FONTS.
        )
        title_font.setBold(True)  # Make the chart title bold.
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the title text.
        title_label.setStyleSheet(
            f"color: {theme_COLORS.get('text_light', '#E0E0E0')}; background: transparent; padding-bottom: {SPACING.get('xs','4px')};"  # Light text color, transparent background, and some bottom padding.
        )
        container_layout.addWidget(
            title_label
        )  # Add the title label to the container's layout.

        # If the pyqtgraph library is available, create and configure the plot widget.
        if PYQTGRAPH_AVAILABLE:
            # Configure global pyqtgraph options for background and foreground colors to match the theme.
            pg.setConfigOption(
                "background",
                QColor(
                    theme_COLORS.get("background_medium", "#334155")
                ),  # Set pyqtgraph background.
            )
            pg.setConfigOption(
                "foreground",
                QColor(
                    theme_COLORS.get("text_light_hex", "#f8fafc")
                ),  # Set pyqtgraph foreground (axes, labels).
            )

            plot_widget = pg.PlotWidget()  # Create the pyqtgraph plot widget.
            plot_widget.getPlotItem().getViewBox().setBackgroundColor(
                None  # Make the plot area background transparent to see the frame's background color.
            )
            plot_widget.showGrid(
                x=True,
                y=True,
                alpha=0.2,  # Show grid lines on the chart with some transparency.
            )
            container_layout.addWidget(
                plot_widget  # Add the plot widget to the container's layout.
            )
            chart_container_frame.plot_widget = plot_widget  # Store a reference to the plot widget for easy access when plotting data.
        else:
            # If pyqtgraph is not available, display a placeholder label indicating that graphs are disabled.
            no_graph_label = QLabel("pyqtgraph non disponible")
            no_graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_graph_label.setStyleSheet(
                f"color: {theme_COLORS.get('text_disabled', '#AAAAAA')};"  # Disabled text color from theme.
            )
            container_layout.addWidget(no_graph_label)
            chart_container_frame.plot_widget = None  # No plot widget is available.

        return chart_container_frame  # Return the created chart container frame.

    # Method to load data from the database and update the dashboard UI elements.
    # This is typically called when the dashboard is first shown or when a refresh is needed.
    def load_data(
        self,
    ):
        print("Dashboard: Loading data...")  # Debug message for developers.
        # Initialize variables to hold the data fetched from the database.
        total_clients = 0
        total_products = 0
        total_sales_current_month = 0.0
        low_stock_count = 0
        sales_trend_data = []  # For the sales trend line chart.
        top_products_data = []  # For the top selling products bar chart.

        try:
            conn = get_db_connection()  # Establish a connection to the SQLite database.
            cursor = conn.cursor()  # Create a cursor object to execute SQL queries.

            # --- Fetch data for Summary Cards ---

            # Fetch the total number of customers.
            cursor.execute("SELECT COUNT(id) FROM Customers")
            result = cursor.fetchone()  # Fetch the first row of the query result.
            total_clients = (
                result[0]
                if result and result[0] is not None
                else 0  # Assign the count, or 0 if no result/count is None.
            )

            # Fetch the total number of products.
            cursor.execute("SELECT COUNT(id) FROM Products")
            result = cursor.fetchone()
            total_products = result[0] if result and result[0] is not None else 0

            # Fetch the total sales amount for the current month.
            current_month_str = datetime.datetime.now().strftime(
                "%Y-%m"  # Get the current year and month in 'YYYY-MM' format.
            )
            cursor.execute(
                "SELECT SUM(total_amount) FROM Sales WHERE strftime('%Y-%m', sale_date) = ?",  # SQL query to sum 'total_amount' for sales in the current month.
                (
                    current_month_str,
                ),  # Pass the current month string as a parameter to the query.
            )
            result = cursor.fetchone()
            total_sales_current_month = (
                result[0]
                if result and result[0] is not None
                else 0.0  # Assign sum, or 0.0 if no sales/sum is None.
            )

            # Import LOW_STOCK_THRESHOLD from stock_view to maintain consistency in defining "low stock".
            # This threshold is used to count products that are considered to have low stock.
            from views.stock_view import LOW_STOCK_THRESHOLD as DASH_LOW_STOCK

            # Fetch the count of products with low stock.
            # Low stock is defined as quantity_in_stock > 0 AND quantity_in_stock < DASH_LOW_STOCK.
            cursor.execute(
                f"SELECT COUNT(id) FROM Products WHERE quantity_in_stock > 0 AND quantity_in_stock < ?",
                (DASH_LOW_STOCK,),  # Pass the low stock threshold as a parameter.
            )
            result = cursor.fetchone()
            low_stock_count = result[0] if result and result[0] is not None else 0

            conn.close()  # Close the database connection as all queries for cards are done.

            # --- Fetch data for Charts (if pyqtgraph is available) ---
            if PYQTGRAPH_AVAILABLE:
                # Fetch data for the monthly sales trend chart (e.g., last 12 months).
                sales_trend_data = get_monthly_sales_trend(
                    num_months=12  # This function is defined in database.py.
                )
                # Fetch data for the top selling products chart (e.g., top 5 products by quantity sold).
                top_products_data = get_top_selling_products(
                    limit=5  # This function is defined in database.py.
                )

            print("Dashboard: Data fetched successfully.")  # Debug message.

        except (
            Exception
        ) as e:  # Catch any errors that occur during database interaction.
            print(
                f"Dashboard: Error loading data: {e}"
            )  # Print the error message for debugging.
            # Optionally, display an error message to the user on the dashboard itself.

        try:
            # --- Update UI Elements with Fetched Data ---

            # Update the text of the value labels in the summary cards.
            self.total_clients_card.value_label.setText(str(total_clients))
            self.total_products_card.value_label.setText(str(total_products))
            self.total_sales_card.value_label.setText(
                f"{total_sales_current_month:.2f} DA"  # Format sales as currency with 2 decimal places.
            )
            self.low_stock_card.value_label.setText(str(low_stock_count))

            # If pyqtgraph is available, plot the fetched data on the charts.
            if PYQTGRAPH_AVAILABLE:
                self._plot_sales_trend(
                    sales_trend_data  # Call helper method to plot the sales trend.
                )
                self._plot_top_products(
                    top_products_data  # Call helper method to plot the top products.
                )
            print("Dashboard: UI updated.")  # Debug message.
        except Exception as e:  # Catch any errors that occur during UI updates.
            print(f"Dashboard: Error updating UI: {e}")  # Print the error message.

    # Helper method to plot the sales trend data on its chart.
    # Parameters:
    #   data (list of tuples): A list where each tuple is (month_string, total_sales_amount).
    #                          Example: [('2023-01', 1500.00), ('2023-02', 2200.50), ...]
    def _plot_sales_trend(self, data):
        # Check if plotting is possible (pyqtgraph available and plot widget exists).
        if (
            not PYQTGRAPH_AVAILABLE
            or not hasattr(
                self, "sales_trend_plot_widget"
            )  # Check if the sales_trend_plot_widget attribute exists.
            or not self.sales_trend_plot_widget.plot_widget  # Check if the plot_widget within it exists.
        ):
            return  # Exit if plotting prerequisites are not met.

        plot_widget = (
            self.sales_trend_plot_widget.plot_widget
        )  # Get the pyqtgraph PlotWidget instance.
        plot_item = (
            plot_widget.getPlotItem()
        )  # Get the PlotItem from the PlotWidget. This is where data is plotted.
        plot_item.clear()  # Clear any existing plots from the PlotItem to prepare for new data.

        # Disable auto-ranging for axes to set ranges manually, ensuring 0 is the minimum.
        plot_item.enableAutoRange(
            axis="x", enable=False
        )  # Disable auto-ranging for X-axis.
        plot_item.enableAutoRange(
            axis="y", enable=False
        )  # Disable auto-ranging for Y-axis.

        # If no data is available, display a message on the chart and set default axis ranges.
        if not data:
            plot_item.setXRange(0, 1, padding=0)  # Set X-axis range from 0 to 1.
            plot_item.setYRange(0, 1, padding=0)  # Set Y-axis range from 0 to 1.
            # Add a text item to the plot indicating no data.
            plot_item.addItem(
                pg.TextItem(
                    "Aucune donnée de vente disponible.",  # Message to display.
                    color=QColor(
                        theme_COLORS.get("text_disabled", "gray")
                    ),  # Text color from theme.
                )
            )
            return  # Exit the function as there's no data to plot.

        try:
            # Convert month strings from data to numerical timestamps for plotting on a time-series axis.
            # Timestamps are generally seconds since the epoch.
            timestamps = [
                datetime.datetime.strptime(
                    d[0] + "-01",
                    "%Y-%m-%d",  # Assumes 'YYYY-MM' format from DB, appends '-01' for day to create a full date.
                ).timestamp()  # Convert datetime object to a Unix timestamp.
                for d in data
            ]
            # Ensure all sales values are non-negative. Clamp any negative values to 0.
            values = [max(0, d[1]) for d in data]
        except (
            ValueError
        ) as e:  # Catch errors if date parsing fails (e.g., unexpected date format).
            print(
                f"Dashboard: Error parsing date for sales trend: {e}"
            )  # Log the error.
            # Display an error message on the chart.
            plot_item.setXRange(0, 1, padding=0)
            plot_item.setYRange(0, 1, padding=0)
            plot_item.addItem(
                pg.TextItem(
                    "Erreur format date.",
                    color=QColor(
                        theme_COLORS.get("error", "red")
                    ),  # Error text color from theme.
                )
            )
            return  # Exit due to parsing error.

        # Use DateAxisItem for the bottom (X) axis to display dates correctly.
        axis = DateAxisItem(orientation="bottom")
        plot_item.setAxisItems(
            {"bottom": axis}
        )  # Set the custom date axis for the bottom.

        # Manually set the X and Y axis ranges.
        # X-axis (time): Ensure minimum is 0 or the earliest timestamp.
        # Y-axis (sales amount): Ensure minimum is 0.
        min_x = (
            min(timestamps) if timestamps else 0
        )  # Minimum timestamp or 0 if no timestamps.
        max_x = (
            max(timestamps) if timestamps else 1
        )  # Maximum timestamp or 1 if no timestamps.
        plot_item.setXRange(
            max(0, min_x), max(0, max_x), padding=0.05
        )  # Set X-range with a small padding.
        plot_item.setYRange(
            0, max(values) if values else 1, padding=0.1
        )  # Set Y-range from 0 to max sales value, with padding.

        # Define colors for the plot line and symbols from theme.CHART_COLORS or fallback to theme.COLORS.
        pen_color = QColor(
            CHART_COLORS[0] if CHART_COLORS else theme_COLORS.get("primary", "#3498DB")
        )
        symbol_brush_color = QColor(
            CHART_COLORS[0] if CHART_COLORS else theme_COLORS.get("primary", "#3498DB")
        )

        # Plot the sales trend data (timestamps vs. sales values).
        plot_item.plot(
            timestamps,  # X-values (time).
            values,  # Y-values (sales amounts).
            pen=pg.mkPen(color=pen_color, width=2),  # Line style (color and width).
            symbol="o",  # Use circle ('o') symbols for data points.
            symbolBrush=symbol_brush_color,  # Fill color for the symbols.
            symbolSize=6,  # Size of the symbols.
            antialias=True,  # Enable antialiasing for smoother lines and symbols.
        )
        # Set labels for the axes.
        plot_item.setLabel(
            "left",  # Target the left Y-axis.
            "Montant Total (DA)",  # Label text (e.g., Total Amount in Algerian Dinar).
            color=theme_COLORS.get(
                "text_light_hex", "#FFFFFF"
            ),  # Label text color from theme.
        )
        # Set text colors for the axis tick labels.
        plot_item.getAxis("left").setTextPen(
            QColor(
                theme_COLORS.get("text_light_hex", "#FFFFFF")
            )  # Y-axis tick label color.
        )
        plot_item.getAxis("bottom").setTextPen(
            QColor(
                theme_COLORS.get("text_light_hex", "#FFFFFF")
            )  # X-axis (date) tick label color.
        )

    # Helper method to plot the top selling products data as a bar chart.
    # Parameters:
    #   data (list of tuples): A list where each tuple is (product_name, total_quantity_sold).
    #                          Example: [('Laptop X', 50), ('Mouse Y', 120), ...]
    def _plot_top_products(self, data):
        # Check if plotting is possible.
        if (
            not PYQTGRAPH_AVAILABLE
            or not hasattr(
                self, "top_products_plot_widget"
            )  # Check if the attribute exists.
            or not self.top_products_plot_widget.plot_widget  # Check if the plot_widget within it exists.
        ):
            return  # Exit if prerequisites not met.

        plot_widget = self.top_products_plot_widget.plot_widget  # Get the PlotWidget.
        plot_item = plot_widget.getPlotItem()  # Get the PlotItem.
        plot_item.clear()  # Clear any previous plots.

        # Disable auto-ranging for axes to set ranges manually.
        plot_item.enableAutoRange(axis="x", enable=False)
        plot_item.enableAutoRange(axis="y", enable=False)

        # If no data, display a message and set default axis ranges.
        if not data:
            plot_item.setXRange(0, 1, padding=0)
            plot_item.setYRange(0, 1, padding=0)
            plot_item.addItem(
                pg.TextItem(
                    "Aucune donnée produit disponible.",
                    color=QColor(theme_COLORS.get("text_disabled", "gray")),
                )
            )
            return  # Exit if no data.

        # Prepare data for the bar chart.
        # Truncate long product names for better display on the X-axis.
        product_names = [
            item[0][:15] + "..." if len(item[0]) > 15 else item[0]
            for item in data  # Truncate names longer than 15 characters.
        ]
        # Ensure all quantities are non-negative.
        quantities = [max(0, item[1]) for item in data]  # Clamp quantities to be >= 0.
        x_values = list(
            range(len(product_names))
        )  # X-coordinates for the bars (0, 1, 2, ...).

        # Create a list of brushes for the bars, using gradients and cycling through theme.CHART_COLORS.
        bar_brushes = []
        for i in range(len(data)):
            color = QColor(
                CHART_COLORS[
                    i % len(CHART_COLORS)
                ]  # Cycle through available chart colors.
            )
            gradient = QLinearGradient(0, 0, 0, 1)  # Define a vertical linear gradient.
            gradient.setCoordinateMode(
                QGradient.CoordinateMode.ObjectBoundingMode  # Gradient coordinates are relative to the bar's bounding box.
            )
            gradient.setColorAt(
                0, color.lighter(130)
            )  # Lighter shade at the top of the bar.
            gradient.setColorAt(
                1, color.darker(110)
            )  # Darker shade at the bottom of the bar.
            bar_brushes.append(
                QBrush(gradient)
            )  # Add the created gradient brush to the list.

        # Create a BarGraphItem with the prepared data and brushes.
        bg_item = BarGraphItem(
            x=x_values,  # X-positions of the bars.
            height=quantities,  # Heights of the bars (quantities sold).
            width=0.6,  # Width of each bar.
            brushes=bar_brushes,  # List of QBrush objects for each bar.
        )
        plot_item.addItem(bg_item)  # Add the bar graph item to the plot.

        # Manually set the X and Y axis ranges.
        min_x = -0.5  # Start X-axis slightly before the first bar for padding.
        max_x = (
            max(x_values) if x_values else 0
        ) + 0.5  # End X-axis slightly after the last bar.
        plot_item.setXRange(
            min_x, max_x, padding=0
        )  # Set X-range. No additional padding here as it's handled by min_x/max_x.
        plot_item.setYRange(
            0, max(quantities) if quantities else 1, padding=0.1
        )  # Y-range from 0 to max quantity, with padding.

        # Configure the bottom (X) axis to show product names as tick labels.
        axis_bottom = plot_item.getAxis("bottom")
        ticks = [
            list(
                zip(x_values, product_names)
            )  # Create a list of (position, label) pairs for ticks.
        ]
        axis_bottom.setTicks(ticks)  # Set the custom ticks on the X-axis.
        # Set label for the left (Y) axis.
        plot_item.setLabel(
            "left",  # Target the Y-axis.
            "Quantité Vendue",  # Label text.
            color=theme_COLORS.get("text_light_hex", "#FFFFFF"),  # Label text color.
        )
        # Set text colors for axis tick labels.
        plot_item.getAxis("left").setTextPen(
            QColor(
                theme_COLORS.get("text_light_hex", "#FFFFFF")
            )  # Y-axis tick label color.
        )
        axis_bottom.setTextPen(
            QColor(theme_COLORS.get("text_light_hex", "#FFFFFF"))
        )  # X-axis tick label color.
        # Style the bottom axis ticks for better readability (e.g., offset, tick length, font).
        axis_bottom.setStyle(
            tickTextOffset=10,
            tickLength=-5,  # Offset text from axis, adjust tick mark appearance.
        )
        axis_bottom.setTickFont(
            QFont(
                theme_FONTS.get("font_family", "Arial"),
                int(
                    theme_FONTS.get("xs", 9)
                ),  # Smaller font for X-axis tick labels from theme.
            )
        )


if (
    __name__ == "__main__"
):  # This block runs if the script is executed directly (e.g., for testing this view).
    app = QApplication(sys.argv)  # Create the QApplication instance.

    # Determine the project root directory to correctly locate the database file,
    # especially when running this script for testing purposes from within the 'views' directory.
    current_script_dir = os.path.dirname(
        os.path.abspath(__file__)
    )  # Directory of the current script (dashboard_view.py).
    project_root = os.path.dirname(
        current_script_dir
    )  # Parent directory (should be 'sidou2').
    db_file_path = os.path.join(
        project_root, "gestion_commerciale.db"
    )  # Full path to the database file.

    # If the database file doesn't exist, initialize it and add some sample data for testing the dashboard.
    # This is crucial for standalone testing of the dashboard view.
    if not os.path.exists(db_file_path):
        print("Database file not found for dashboard test. Initializing...")
        # Add the project root to sys.path to allow importing modules from other project directories (like 'database').
        sys.path.insert(0, project_root)
        from database.database import (  # Import database functions.
            initialize_database,
            add_product,
            add_customer,
            add_sale,
        )

        initialize_database()  # Create database tables if they don't exist.
        # Add sample data only if no sales trend data exists (indicative of an empty or newly initialized database).
        # This prevents re-adding sample data every time the test is run if the DB already has data.
        if not get_monthly_sales_trend():
            # Add a sample customer and products.
            c1 = add_customer("Test Client Dash", phone="0101010101")
            p1 = add_product("Produit Alpha", "Desc", "CatDash", 10, 20, 100)
            p2 = add_product("Produit Beta", "Desc", "CatDash", 5, 15, 50)

            if (
                p1 and p2 and c1 is not None
            ):  # Ensure sample objects were created successfully.
                # Add sample sales with specific dates to test the sales trend chart.
                add_sale(  # Sale 1
                    [
                        {"product_id": p1, "quantity": 2, "price_at_sale": 20},
                        {"product_id": p2, "quantity": 5, "price_at_sale": 15},
                    ],
                    customer_id=c1,
                    sale_date_str="2023-01-15 10:00:00",  # Older sale (example date).
                )
                add_sale(  # Sale 2
                    [{"product_id": p1, "quantity": 3, "price_at_sale": 20}],
                    customer_id=c1,
                    sale_date_str="2023-02-10 12:00:00",  # More recent sale (example date).
                )
            elif (
                p1 and p2
            ):  # Fallback if customer creation failed, add sales without customer.
                add_sale(
                    [
                        {"product_id": p1, "quantity": 2, "price_at_sale": 20},
                        {"product_id": p2, "quantity": 5, "price_at_sale": 15},
                    ],
                    sale_date_str="2023-01-15 10:00:00",
                )
                add_sale(
                    [{"product_id": p1, "quantity": 3, "price_at_sale": 20}],
                    sale_date_str="2023-02-10 12:00:00",
                )

    else:  # If the database file already exists.
        print("Database file found for dashboard test.")
        # Ensure project root is in sys.path for imports if run directly.
        sys.path.insert(0, project_root)

    from theme import (
        apply_global_style,
    )  # Import function to apply the global application theme.

    apply_global_style(app)  # Apply the theme to the QApplication instance.

    # Create and show the DashboardView widget for testing.
    dashboard_widget = DashboardView()
    dashboard_widget.setWindowTitle(
        "Test Tableau de Bord"
    )  # Set the window title for the test window.
    dashboard_widget.resize(900, 700)  # Set a default size for the test window.
    dashboard_widget.show()  # Display the dashboard widget.

    sys.exit(app.exec())  # Start the Qt application event loop.
