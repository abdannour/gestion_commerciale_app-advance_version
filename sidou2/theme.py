# Updated content for sidou2/theme.py
# This file centralizes the visual styling elements for the PyQt6 application.
# It defines colors, fonts, spacing, radii, and stylesheets for various UI components,
# promoting a consistent look and feel across the entire application.
# Such centralization is crucial for maintainability and team collaboration in a group project.

import os  # Provides functions for interacting with the operating system, used here for path manipulation (e.g., for icons).
from PyQt6.QtGui import (
    QColor,  # Represents colors, supporting various formats including hex and RGB.
    QFont,  # Specifies font properties like family, size, weight.
    QIcon,  # Handles icons for widgets.
)

# --- Directory for Icons ---
# Constructs an absolute path to the 'icons' subdirectory, relative to this theme.py file.
# os.path.abspath(__file__) gets the absolute path of the current script (theme.py).
# os.path.dirname(...) gets the directory part of that path.
# os.path.join(...) then combines this directory with 'icons' to form the full path.
# This robust approach ensures icons are found regardless of where the main application script is executed from.
ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

# --- Color Palette (COLORS) ---
# A dictionary defining various colors used throughout the application.
# Colors are specified in hexadecimal string format (e.g., "#RRGGBB").
# Grouping colors by function (primary, secondary, accent, grayscale, UI elements)
# improves organization and makes it easier to understand their intended use.
# For a university project, a well-defined and consistently used color palette
# demonstrates attention to UI/UX design principles.
COLORS = {
    # Primary colors: Often used for branding, main actions, and highlights.
    "primary": "#6366f1",  # A modern indigo/purple, good for primary actions.
    "primary_light": "#818cf8",  # A lighter shade for hover states or secondary elements.
    "primary_dark": "#4f46e5",  # A darker shade for pressed states or stronger emphasis.
    "primary_bg": "#eef2ff",  # A very light background related to the primary color, useful for subtle highlights or focused inputs.
    # Secondary colors: Used for complementary elements, success states, or alternative actions.
    "secondary": "#10b981",  # A vibrant green, often associated with success.
    "secondary_light": "#34d399",
    "secondary_dark": "#059669",
    "secondary_bg": "#d1fae5",
    # Accent and status colors: For highlights, and conveying information like success, warnings, errors.
    "accent": "#8b5cf6",  # A violet accent, can be used for specific highlights.
    "success": "#10b981",  # Green for success messages, operations. Often same as secondary.
    "success_dark": "#059669",
    "success_bg": "#ecfdf5",  # Light background for success messages/badges.
    "warning": "#f59e0b",  # Amber/yellow for warnings.
    "warning_dark": "#d97706",
    "warning_bg": "#fffbeb",
    "error": "#ef4444",  # Red for errors, destructive actions.
    "error_dark": "#dc2626",
    "error_bg": "#fef2f2",
    "info": "#3b82f6",  # Blue for informational messages.
    "info_dark": "#2563eb",
    "info_bg": "#eff6ff",
    # Grayscale palette: Essential for text, backgrounds, borders, and general UI structure.
    # A good range of grays allows for nuanced design.
    "white": "#ffffff",
    "black": "#0f172a",  # A very dark gray (slate), often better for text than pure #000000.
    "gray_50": "#f8fafc",  # Lightest gray, almost white.
    "gray_100": "#f1f5f9",
    "gray_200": "#e2e8f0",
    "gray_300": "#cbd5e1",  # Light-medium gray, good for borders.
    "gray_400": "#94a3b8",  # Medium gray, good for secondary text or disabled states.
    "gray_500": "#64748b",
    "gray_600": "#475569",
    "gray_700": "#334155",  # Dark gray, can be used for backgrounds.
    "gray_800": "#1e293b",  # Very dark gray.
    "gray_900": "#0f172a",  # Darkest gray, same as "black" here.
    # Dashboard specific colors: Example of how colors might be themed for a specific view.
    # These can be aliases to existing colors or unique shades.
    # "background_dark" and "background_medium" are used in DashboardView.
    "background_dark": "#1e293b",  # Dark background for the dashboard content area.
    "background_medium": "#334155",  # Slightly lighter dark for elements within the dashboard (e.g., chart frames).
    "text_light": "#f8fafc",  # Light text color for use on dark backgrounds.
    "text_light_hex": "#f8fafc",  # Explicit hex for pyqtgraph if 'w' (white shortcut) isn't working as expected.
    "text_muted": "#94a3b8",  # For less important text on dark backgrounds.
    "text_subtle": "#cbd5e1",  # For very subtle text or hints on dark backgrounds.
    # General UI element colors: Define the overall appearance of the application.
    "background": "#f8fafc",  # Main window background (light theme).
    "surface": "#ffffff",  # Background for elements like cards, inputs, dialogs (on top of main background).
    "surface_variant": "#f1f5f9",  # A slightly different surface color, e.g., for table headers.
    "text_primary": "#0f172a",  # Main text color (dark, for light backgrounds).
    "text_secondary": "#475569",  # Secondary text color (less emphasis).
    "text_tertiary": "#64748b",  # Tertiary text color (even less emphasis).
    "text_disabled": "#94a3b8",  # Text color for disabled UI elements.
    "border": "#e2e8f0",  # Default border color for inputs, tables, cards.
    "border_strong": "#cbd5e1",  # A stronger border color for more emphasis.
    "divider": "#f1f5f9",  # Color for dividers/separators (e.g., table grid lines).
    "hover": "#f8fafc",  # Background color on hover (subtle, might need to be darker than this example if on a similar background).
    "pressed": "#f1f5f9",  # Background color when an element is pressed.
    "focus": "#eef2ff",  # Highlight color for focused elements (e.g., input border, often related to primary_bg).
}

# --- Fonts (FONTS) ---
# A dictionary defining font families and sizes.
# Sizes are typically in points (pt) for Qt.
# Consistent typography is key to a professional-looking application.
# For a group project, agreeing on these font scales helps maintain UI consistency.
FONTS = {
    # Default font family for the application. 'Arial' is widely available.
    # Consider system fonts or bundling a specific font for a more unique look.
    "font_family": "Arial",
    # Typography stacks: Provide fallback fonts if the primary font isn't available.
    # This is more common in web CSS, but the concept can be adapted. Qt usually falls back gracefully.
    "family_primary": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif",  # Common system UI fonts.
    "family_mono": "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, 'Courier New', monospace",  # Monospaced fonts for code or tabular data.
    # Old font size definitions (can be deprecated or integrated into the new scale below)
    "font_size_small": 8,
    "font_size_medium": 10,
    "font_size_large": 12,
    "font_size_xlarge": 16,
    "font_size_title": 20,
    # Specific element font properties
    "sidebar_item_height": 55,  # Defines the height of items in the sidebar QListWidget.
    # Scaled font sizes (inspired by utility CSS frameworks like Tailwind CSS)
    # Using a typographic scale (xs, sm, base, md, lg, xl, etc.) provides a consistent hierarchy.
    # Values are points (pt).
    "xs": 9,  # Extra small (e.g., for captions, fine print)
    "sm": 10,  # Small (e.g., for secondary text, small labels)
    "base": 11,  # Standard body text size, used as default for many elements.
    "md": 12,  # Medium (e.g., for slightly larger body text, input fields)
    "lg": 14,  # Large (e.g., for subheadings, important labels)
    "xl": 16,  # Extra large (e.g., for titles, prominent text)
    "2xl": 18,
    "3xl": 20,  # For headings
    "4xl": 24,  # For major headings or display text
    "5xl": 28,
    "6xl": 32,  # Largest (e.g., for hero titles on a dashboard)
    # Semantic font sizes: Aliases for clarity in code, mapping to the scale above.
    # This makes it easier to understand the intended use of a font size.
    "caption": 9,  # e.g., small text below an image or chart.
    "body_small": 10,  # Smaller body text.
    "body": 11,  # Default body text.
    "body_large": 12,  # Larger body text.
    "button": 12,  # Font size for text on buttons.
    "subtitle": 14,  # Subtitles for sections.
    "title": 16,  # Titles for views or major components.
    "heading": 20,  # Main headings.
    "display": 24,  # Large display text, e.g., for dashboard titles.
    # Component-specific font sizes: For fine-tuning specific UI elements.
    "card_title_size": 12,  # Specific size for titles within dashboard cards.
    "card_value_size": 22,  # Specific size for main values (KPIs) within dashboard cards.
    "chart_widget_title_size": 12,  # For titles of chart containers/widgets on the dashboard.
    "chart_title_size": "14pt",  # For pyqtgraph chart titles (can be string with 'pt' unit for pyqtgraph).
}

# --- Spacing Scale (SPACING) ---
# Defines a consistent spacing scale for margins, padding.
# Values are strings with 'px' (pixels). Using a scale (xs, sm, md, etc.)
# helps maintain visual rhythm and consistency.
# For a project presentation, consistent spacing contributes significantly to a polished look.
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "20px",
    "2xl": "24px",
    "3xl": "32px",
    "4xl": "40px",
    "5xl": "48px",
}

# --- Border Radius (RADIUS) ---
# Defines common border radius values for rounded corners on UI elements.
# Values are strings with 'px'. Rounded corners give a softer, more modern feel.
RADIUS = {
    "none": "0px",  # No border radius (sharp corners).
    "sm": "6px",  # Small radius.
    "md": "8px",  # Medium radius (common for inputs, buttons).
    "lg": "12px",  # Large radius (common for cards, containers).
    "xl": "16px",  # Extra large radius.
    "2xl": "20px",
    "full": "9999px",  # For creating pills or fully rounded elements (like badges).
}

# --- Shadows (SHADOWS) ---
# Defines box-shadow like effects. Qt's QSS doesn't directly support CSS box-shadow.
# These are primarily for reference or for programmatic use with QGraphicsDropShadowEffect.
# Using shadows can add depth and hierarchy to the UI.
SHADOWS = {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",  # Subtle shadow.
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",  # Standard shadow.
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",  # Larger shadow.
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",  # Prominent shadow.
}

# --- Styles (STYLES) ---
# A dictionary of Qt Stylesheet (QSS) strings for various UI components.
# QSS is similar to CSS but with some differences in properties and syntax.
# Using f-strings allows embedding color, font, spacing, and radius values
# from the dictionaries defined above, making styles dynamic and themeable.
# This section is critical for the visual presentation of the project.
# Well-structured QSS makes the UI appealing and user-friendly.
STYLES = {
    # Style for the main application window (QMainWindow or top-level QWidget).
    "main_window": f"""
        background-color: {COLORS['background']}; /* Light background for the main window. */
        color: {COLORS['text_primary']}; /* Default text color. */
        font-family: {FONTS['font_family']}; /* Default application font. */
    """,
    # Style for the navigation sidebar (QListWidget).
    "sidebar": f"""
        background-color: {COLORS['gray_900']}; /* Dark background for the sidebar, creating contrast. */
        color: {COLORS['white']}; /* Light text color for readability on dark background. */
        border: none; /* No border around the sidebar itself. */
        padding: {SPACING['xl']} {SPACING['md']}; /* Vertical and horizontal padding within the sidebar. */
    """,
    # Style for items within the sidebar (QListWidget::item).
    "sidebar_item": f"""
        QListWidget::item {{
            color: {COLORS['gray_300']}; /* Default text color for sidebar items. */
            padding: {SPACING['md']} {SPACING['lg']}; /* Padding around item content (text and icon). */
            border-radius: {RADIUS['md']}; /* Rounded corners for each item. */
            font-size: {FONTS['body_large']}pt; /* Font size for item text. */
            /* font-weight: 500; Note: Direct font-weight in QSS for QListWidget::item can be inconsistent.
               Consider a custom delegate or styling the QLabel inside a custom widget item for full control. */
            margin-bottom: {SPACING['xs']}; /* Space below each item, creating separation. */
            border: none; /* No border around items themselves. */
        }}
        QListWidget::item:hover {{
            background-color: {COLORS['gray_800']}; /* Background color when mouse hovers over an item. */
            color: {COLORS['white']}; /* Text color on hover. */
        }}
        QListWidget::item:selected {{
            background-color: {COLORS['primary']}; /* Background color for the selected item (active page). */
            color: {COLORS['white']}; /* Text color for the selected item. */
            /* font-weight: 600; Bolder font for selected item (see note above about font-weight). */
        }}
    """,
    # Style for main titles (e.g., view titles).
    "title": f"""
        font-size: {FONTS['4xl']}pt; /* Large font size for main titles. */
        font-weight: bold; /* Use 'bold' keyword for wider compatibility than numeric weights in QSS. */
        color: {COLORS['text_primary']}; /* Primary text color. */
        margin-bottom: {SPACING['xl']}; /* Space below the title. */
        /* letter-spacing: -0.025em; CSS-like property, might not be fully supported or have the desired effect in QSS. */
        /* line-height: 1.2; CSS-like property, informational for QSS. */
    """,
    # Style for subtitles.
    "subtitle": f"""
        font-size: {FONTS['xl']}pt;
        font-weight: bold;
        color: {COLORS['text_primary']};
        margin-bottom: {SPACING['md']};
        /* line-height: 1.4; */
    """,
    # Style for card-like containers (QFrame).
    "card": f"""
        background-color: {COLORS['surface']}; /* Background color for cards (typically white or light gray). */
        border-radius: {RADIUS['xl']}; /* Large border radius for a modern, soft look. */
        padding: {SPACING['2xl']}; /* Generous padding inside cards. */
        border: 1px solid {COLORS['border']}; /* Subtle border for cards. */
        /* box-shadow: {SHADOWS['sm']}; Qt QSS doesn't directly support CSS box-shadow.
           Use QGraphicsDropShadowEffect programmatically for shadows on QFrames or QWidgets. */
    """,
    # --- Button Styles ---
    # Defining styles for different types of buttons (primary, secondary, destructive)
    # helps users understand the action associated with each button.
    "button_primary": f"""
        QPushButton {{
            background-color: {COLORS['primary']}; /* Primary button background color. */
            color: {COLORS['white']}; /* Text color for primary button (light on dark). */
            border: none; /* No border for a cleaner look. */
            border-radius: {RADIUS['lg']}; /* Rounded corners. */
            padding: {SPACING['md']} {SPACING['2xl']}; /* Padding (vertical, horizontal) for a good click area. */
            font-weight: bold;
            font-size: {FONTS['button']}pt;
            min-height: 40px; /* Minimum button height for consistent size. */
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_dark']}; /* Darker background on hover for feedback. */
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_dark']}; /* Same as hover or slightly darker when pressed. */
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_300']}; /* Appearance for disabled state (less prominent). */
            color: {COLORS['text_disabled']};
        }}
    """,
    "button_secondary": f"""
        QPushButton {{
            background-color: {COLORS['surface']}; /* Typically lighter background than primary. */
            color: {COLORS['text_primary']}; /* Darker text color. */
            border: 1px solid {COLORS['border_strong']}; /* Visible border to differentiate from primary. */
            border-radius: {RADIUS['lg']};
            padding: {SPACING['md']} {SPACING['2xl']};
            font-weight: bold;
            font-size: {FONTS['button']}pt;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['gray_50']}; /* Slight change on hover. */
            border-color: {COLORS['gray_400']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['gray_100']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_100']};
            color: {COLORS['text_disabled']};
            border-color: {COLORS['gray_200']};
        }}
    """,
    "button_destructive": f"""
        QPushButton {{
            background-color: {COLORS['error']}; /* Error color (red) for actions like delete. */
            color: {COLORS['white']};
            border: none;
            border-radius: {RADIUS['lg']};
            padding: {SPACING['md']} {SPACING['2xl']};
            font-weight: bold;
            font-size: {FONTS['button']}pt;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['error_dark']}; /* Darker error color on hover. */
        }}
        QPushButton:pressed {{
            background-color: {COLORS['error_dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_300']};
            color: {COLORS['text_disabled']};
        }}
    """,
    # button_success style
    "button_success": f"""
        QPushButton {{
            background-color: {COLORS['secondary']}; /* Green color for success actions */
            color: {COLORS['white']};
            border: none;
            border-radius: {RADIUS['lg']};
            padding: {SPACING['md']} {SPACING['2xl']};
            font-weight: bold;
            font-size: {FONTS['button']}pt;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['secondary_dark']}; /* Darker green on hover */
        }}
        QPushButton:pressed {{
            background-color: {COLORS['secondary_dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_300']};
            color: {COLORS['text_disabled']};
        }}
    """,
    # Ghost button: transparent background, often used for less prominent actions.
    "button_ghost": f"""
        QPushButton {{
            background-color: transparent; /* No background. */
            color: {COLORS['text_primary']};
            border: none;
            border-radius: {RADIUS['lg']};
            padding: {SPACING['md']} {SPACING['2xl']};
            font-weight: 500; /* Normal or medium weight for ghost buttons. */
            font-size: {FONTS['button']}pt;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['hover']}; /* Subtle background on hover. */
        }}
        QPushButton:pressed {{
            background-color: {COLORS['pressed']};
        }}
    """,
    # --- Input Field Styles (QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox) ---
    # Consistent styling for all input types is important for usability.
    "input": f"""
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            border: 1px solid {COLORS['border']}; /* Default border. */
            border-radius: {RADIUS['md']}; /* Rounded corners. */
            padding: {SPACING['sm']} {SPACING['lg']}; /* Padding (top/bottom, left/right) for text. */
            background-color: {COLORS['surface']}; /* Background color. */
            color: {COLORS['text_primary']}; /* Text color. */
            font-size: {FONTS['body']}pt; /* Font size for input text. */
            min-height: 35px; /* Unified minimum height for a consistent form layout. */
            selection-background-color: {COLORS['primary_bg']}; /* Background color of selected text. */
            selection-color: {COLORS['text_primary']}; /* Color of selected text. */
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {COLORS['primary']}; /* Thicker, primary color border on focus to indicate active input. */
            background-color: {COLORS['focus']}; /* Subtle background change on focus. */
            /* outline: none; Not a standard Qt QSS property, focus indication is handled by border change. */
            /* Adjust padding to account for the thicker border, maintaining inner content alignment.
               calc() might not be fully supported in all Qt versions/contexts for padding,
               so ensure this works or set slightly different padding values. */
            padding: calc({SPACING['sm']} - 1px) calc({SPACING['lg']} - 1px);
        }}
        QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: {COLORS['gray_50']}; /* Disabled state appearance. */
            color: {COLORS['text_disabled']};
            border-color: {COLORS['gray_200']};
        }}

        /* QComboBox specific styling for the dropdown arrow and list. */
        QComboBox::drop-down {{
            subcontrol-origin: padding; /* Position relative to padding box. */
            subcontrol-position: top right; /* Position of the dropdown button. */
            width: 20px; /* Width of the dropdown button area. */
            border-left-width: 1px; /* Separator line before the arrow. */
            border-left-color: {COLORS['border']};
            border-left-style: solid;
            border-top-right-radius: {RADIUS['md']}; /* Match parent input's border radius. */
            border-bottom-right-radius: {RADIUS['md']};
            background-color: {COLORS['gray_50']}; /* Background of dropdown button. */
        }}
        QComboBox::down-arrow {{
            /* Use an SVG icon for the arrow. Ensure path uses forward slashes for QSS.
               os.path.join().replace(os.sep, '/') is a robust way to create platform-independent paths for QSS. */
            image: url('{os.path.join(ICON_DIR, "chevron-down-svgrepo-com.svg").replace(os.sep, '/')}');
            width: 10px; /* Size of the arrow icon. */
            height: 10px;
        }}
        QComboBox::down-arrow:on {{ /* Style when the popup (dropdown list) is open. */
            top: 1px; /* Slight position adjustment for visual feedback. */
            left: 1px;
        }}
        QComboBox QAbstractItemView {{ /* Style for the dropdown list itself. */
            border: 1px solid {COLORS['border']};
            background-color: {COLORS['surface']};
            color: {COLORS['text_primary']};
            selection-background-color: {COLORS['primary_bg']}; /* Background of selected item in the list. */
            selection-color: {COLORS['primary_dark']}; /* Text color of selected item in the list. */
            padding: {SPACING['xs']}; /* Padding within the dropdown list. */
        }}

        /* QSpinBox and QDoubleSpinBox up/down buttons. */
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border; /* Position relative to the border box. */
            width: 16px; /* Width of the button area. */
            border-left-width: 1px; /* Separator line. */
            border-left-color: {COLORS['border']};
            border-left-style: solid;
            border-radius: 0; /* No individual radius if part of a larger input styling. */
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-position: top right; /* Position of the up button. */
            image: url('{os.path.join(ICON_DIR, "chevron-up-svgrepo-com.svg").replace(os.sep, '/')}'); /* Up arrow icon. */
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-position: bottom right; /* Position of the down button. */
            image: url('{os.path.join(ICON_DIR, "chevron-down-svgrepo-com.svg").replace(os.sep, '/')}'); /* Down arrow icon. */
        }}
    """,
    # --- Table Styles (QTableWidget) ---
    "table": f"""
        QTableWidget {{
            border: 1px solid {COLORS['border']}; /* Border around the table. */
            border-radius: {RADIUS['lg']}; /* Rounded corners for the table container. */
            background-color: {COLORS['surface']}; /* Background of the table. */
            gridline-color: {COLORS['divider']}; /* Color of grid lines between cells. */
            color: {COLORS['text_primary']}; /* Default text color in cells. */
            selection-background-color: {COLORS['primary_bg']}; /* Background of selected cells/rows. */
            font-size: {FONTS['body']}pt; /* Font size for cell content. */
        }}
        QTableWidget::item {{
            padding: {SPACING['md']}; /* Padding within each cell. */
            border-bottom: 1px solid {COLORS['divider']}; /* Horizontal grid line below item. */
            border-right: 1px solid {COLORS['divider']}; /* Vertical grid line to the right of item. */
            /* Note: QTableWidget's gridline-color often handles this better globally.
               Individual item borders might be redundant or conflict. */
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS['primary']}; /* Selected item background. */
            color: {COLORS['white']}; /* Selected item text color. */
        }}
        QTableWidget::item:hover {{
            background-color: {COLORS['hover']}; /* Hover effect for items. */
        }}

        /* Table Header Styles (QHeaderView::section) */
        QHeaderView::section {{
            background-color: {COLORS['surface_variant']}; /* Header background color. */
            color: {COLORS['text_secondary']}; /* Header text color. */
            padding: {SPACING['lg']} {SPACING['md']}; /* Header padding (vertical, horizontal). */
            font-weight: bold;
            font-size: {FONTS['body_small']}pt;
            text-transform: uppercase; /* Uppercase header text for a formal look. */
            letter-spacing: 0.5px; /* Slight letter spacing (CSS-like, QSS support may vary). */
            border: none; /* Remove default borders from header sections. */
            border-bottom: 2px solid {COLORS['border_strong']}; /* Stronger bottom border for header. */
            border-right: 1px solid {COLORS['divider']}; /* Vertical separator for header sections. */
        }}
        QHeaderView::section:first {{ /* First header section */
            border-top-left-radius: {RADIUS['lg']}; /* Rounded corner for the first header section to match table. */
        }}
        QHeaderView::section:last {{ /* Last header section */
            border-top-right-radius: {RADIUS['lg']}; /* Rounded corner for the last header section. */
            border-right: none; /* No right border for the last header section. */
        }}

        /* Top-left corner button of the table (often empty, but can be styled). */
        QTableCornerButton::section {{
            background-color: {COLORS['surface_variant']};
            border: none;
            border-bottom: 2px solid {COLORS['border_strong']};
            border-right: 1px solid {COLORS['divider']};
            border-top-left-radius: {RADIUS['lg']}; /* Match table's top-left corner. */
        }}
    """,
    # --- Specific Styles (can extend or override general input styles if needed) ---
    # These provide examples if a widget needs styling different from the generic "input" style.
    # Often, the general "input" style is sufficient.
    "line_edit_style": f"""
        QLineEdit {{
            border: 1px solid {COLORS['gray_300']}; /* Consistent with "input" or specific. */
            border-radius: {RADIUS['md']};
            padding: {SPACING['sm']} {SPACING['md']};
            background-color: {COLORS['white']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['base']}pt;
            min-height: 35px;
            selection-background-color: {COLORS['primary']};
            selection-color: {COLORS['white']};
        }}
        QLineEdit:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['primary_bg']};
            border-width: 2px; /* Make focus border thicker. */
            padding: calc({SPACING['sm']} - 1px) calc({SPACING['md']} - 1px); /* Adjust padding. */
        }}
        QLineEdit:disabled {{
            background-color: {COLORS['gray_100']};
            color: {COLORS['text_disabled']};
            border-color: {COLORS['gray_200']};
        }}
    """,
    "combo_box_style": f"""
        QComboBox {{
            border: 1px solid {COLORS['gray_300']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['sm']} {SPACING['md']};
            padding-right: 25px; /* Extra padding on the right for the arrow. */
            background-color: {COLORS['white']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['base']}pt;
            min-height: 35px;
        }}
        QComboBox:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['primary_bg']};
            border-width: 2px;
            /* Adjust padding, including right padding for arrow. */
            padding: calc({SPACING['sm']} - 1px) calc({SPACING['md']} - 1px);
            padding-right: calc(25px - 1px);
        }}
        QComboBox:disabled {{
            background-color: {COLORS['gray_100']};
            color: {COLORS['text_disabled']};
            border-color: {COLORS['gray_200']};
        }}
        /* Dropdown arrow styling (copied from general input style for consistency). */
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: {COLORS['gray_300']}; /* Match border or specific. */
            border-left-style: solid;
            border-top-right-radius: {RADIUS['md']};
            border-bottom-right-radius: {RADIUS['md']};
            background-color: {COLORS['gray_100']}; /* Slightly different background for button. */
        }}
        QComboBox::down-arrow {{
            image: url('{os.path.join(ICON_DIR, "chevron-down-svgrepo-com.svg").replace(os.sep, '/')}');
            width: 10px;
            height: 10px;
        }}
        /* Dropdown list style. */
        QComboBox QAbstractItemView {{
            border: 1px solid {COLORS['border_strong']}; /* Stronger border for the popup list. */
            background-color: {COLORS['white']};
            color: {COLORS['text_primary']};
            selection-background-color: {COLORS['primary_bg']}; /* Background of selected item in the list. */
            selection-color: {COLORS['primary_dark']}; /* Text color of selected item in the list. */
            padding: {SPACING['xs']}; /* Padding within the dropdown list. */
        }}

        /* QSpinBox and QDoubleSpinBox up/down buttons. */
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border; /* Position relative to the border box. */
            width: 16px; /* Width of the button area. */
            border-left-width: 1px; /* Separator line. */
            border-left-color: {COLORS['border']};
            border-left-style: solid;
            border-radius: 0; /* No individual radius if part of a larger input styling. */
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-position: top right; /* Position of the up button. */
            image: url('{os.path.join(ICON_DIR, "chevron-up-svgrepo-com.svg").replace(os.sep, '/')}'); /* Up arrow icon. */
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-position: bottom right; /* Position of the down button. */
            image: url('{os.path.join(ICON_DIR, "chevron-down-svgrepo-com.svg").replace(os.sep, '/')}'); /* Down arrow icon. */
        }}
    """,
    # --- GroupBox Style (QGroupBox) ---
    # GroupBoxes are useful for visually grouping related controls.
    "group_box": f"""
        QGroupBox {{
            border: 1px solid {COLORS['border']}; /* Border around the groupbox. */
            border-radius: {RADIUS['lg']}; /* Rounded corners for the groupbox. */
            margin-top: {SPACING['xl']}; /* Top margin to make space for the title if it's drawn "on top" of the border. */
            font-weight: bold;
            font-size: {FONTS['subtitle']}pt; /* Font for the groupbox title. */
            color: {COLORS['text_primary']};
            padding: {SPACING['lg']}; /* Padding inside the groupbox, below title area. */
            padding-top: {SPACING['2xl']}; /* More padding at the top to accommodate the title nicely within the content area. */
        }}
        QGroupBox::title {{
            subcontrol-origin: margin; /* Position title relative to margin (or padding, depending on desired effect). */
            subcontrol-position: top left; /* Place title at the top left. */
            padding: 0 {SPACING['md']}; /* Horizontal padding for the title text to not touch the border directly. */
            margin-left: {SPACING['lg']}; /* Indent title from the left edge of the GroupBox. */
            background-color: {COLORS['background']}; /* Background of title should match window/parent background for a "cut-out" effect. */
            color: {COLORS['text_primary']};
            font-size: {FONTS['subtitle']}pt; /* Ensure title font matches GroupBox font settings. */
            font-weight: bold;
        }}
    """,
    # --- Label Styles (QLabel) ---
    "label": f"""
        QLabel {{
            color: {COLORS['text_primary']}; /* Default label text color. */
            font-size: {FONTS['body']}pt; /* Default label font size. */
            /* line-height: 1.5; Informational, Qt might not use this directly from QSS for QLabel for layout. */
            background-color: transparent; /* Ensure labels don't have unexpected backgrounds. */
        }}
    """,
    "label_secondary": f"""
        QLabel {{
            color: {COLORS['text_secondary']}; /* For less important labels. */
            font-size: {FONTS['body_small']}pt;
            background-color: transparent;
        }}
    """,
    "label_bold": f"""
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: {FONTS['body']}pt;
            font-weight: bold; /* Bold label text. */
            background-color: transparent;
        }}
    """,
    # --- Status Badges (Styled QLabels) ---
    # Badges are small, colored labels used to indicate status or categories.
    "badge_success": f"""
        QLabel {{
            background-color: {COLORS['success_bg']}; /* Background for success badge. */
            color: {COLORS['secondary_dark']}; /* Text color for success badge. */
            border-radius: {RADIUS['full']}; /* Pill shape (fully rounded). */
            padding: {SPACING['xs']} {SPACING['md']}; /* Padding (vertical, horizontal). */
            font-size: {FONTS['caption']}pt; /* Small font for badges. */
            font-weight: bold;
            text-transform: uppercase; /* Uppercase text for emphasis. */
            letter-spacing: 0.5px; /* Slight letter spacing. */
        }}
    """,
    "badge_warning": f"""
        QLabel {{
            background-color: {COLORS['warning_bg']};
            color: {COLORS['warning_dark']};
            border-radius: {RADIUS['full']};
            padding: {SPACING['xs']} {SPACING['md']};
            font-size: {FONTS['caption']}pt;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
    """,
    "badge_error": f"""
        QLabel {{
            background-color: {COLORS['error_bg']};
            color: {COLORS['error_dark']};
            border-radius: {RADIUS['full']};
            padding: {SPACING['xs']} {SPACING['md']};
            font-size: {FONTS['caption']}pt;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
    """,
    "badge_info": f"""
        QLabel {{
            background-color: {COLORS['info_bg']};
            color: {COLORS['info_dark']};
            border-radius: {RADIUS['full']};
            padding: {SPACING['xs']} {SPACING['md']};
            font-size: {FONTS['caption']}pt;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
    """,
    # --- Progress Bars (QProgressBar) ---
    "progress_bar": f"""
        QProgressBar {{
            border: none; /* Or 1px solid {COLORS['border']} for a subtle border. */
            border-radius: {RADIUS['full']}; /* Fully rounded for a pill shape. */
            background-color: {COLORS['gray_200']}; /* Background of the bar track (the unfilled part). */
            text-align: center; /* Center the percentage text. */
            font-size: {FONTS['body_small']}pt;
            font-weight: 500; /* Normal or medium weight for percentage text. */
            color: {COLORS['text_secondary']}; /* Color of the percentage text. */
            min-height: 20px; /* Ensure visibility and decent height. */
        }}
        QProgressBar::chunk {{ /* The filled part of the progress bar. */
            background-color: {COLORS['primary']}; /* Color of the progress itself. */
            border-radius: {RADIUS['full']}; /* Match parent for a smooth pill shape. */
        }}
    """,
    # --- Scrollbars (QScrollBar) ---
    # Custom scrollbar styles can significantly improve the UI's polish.
    "scrollbar": f"""
        QScrollBar:vertical {{
            border: none; /* No border around the scrollbar. */
            background-color: {COLORS['gray_100']}; /* Background of the scrollbar track. */
            width: 10px; /* Width of the vertical scrollbar. */
            margin: 0px 0px 0px 0px; /* No margins. */
            border-radius: 5px; /* Slightly rounded track. */
        }}
        QScrollBar::handle:vertical {{ /* The draggable part of the scrollbar. */
            background-color: {COLORS['gray_400']}; /* Color of the scrollbar handle. */
            min-height: 20px; /* Minimum height of the handle. */
            border-radius: 5px; /* Rounded handle. */
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {COLORS['gray_500']}; /* Handle color on hover. */
        }}
        /* Hide the add/sub line buttons (the arrows at the ends of the scrollbar). */
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px; /* Effectively hide them by setting size to 0. */
            width: 0px;
        }}
        /* Area above/below handle (the track pages). */
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none; /* Make them transparent. */
        }}

        /* Horizontal Scrollbar (similar styling). */
        QScrollBar:horizontal {{
            border: none;
            background-color: {COLORS['gray_100']};
            height: 10px;
            margin: 0px 0px 0px 0px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {COLORS['gray_400']};
            min-width: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {COLORS['gray_500']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
            height: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
    """,
    # --- Tooltips (QToolTip) ---
    "tooltip": f"""
        QToolTip {{
            background-color: {COLORS['gray_800']}; /* Darker background for tooltips for contrast. */
            color: {COLORS['white']}; /* Light text. */
            border: 1px solid {COLORS['gray_700']}; /* Subtle border. */
            border-radius: {RADIUS['sm']}; /* Smaller radius for tooltips. */
            padding: {SPACING['sm']}; /* Consistent padding. */
            font-size: {FONTS['body_small']}pt; /* Font size for tooltip text. */
            opacity: 230; /* Slight transparency (0-255 range for Qt). Opacity might need to be set programmatically or may not work on all platforms via QSS. */
            /* box-shadow: {SHADOWS['lg']}; Not directly supported by QSS for QToolTip. */
        }}
    """,
}

# --- Colors for Stock Status ---
# Used for visual indication of stock levels (e.g., in StockView table rows).
# Values are QColor objects for direct use with QTableWidgetItem.setBackground/setForeground
# in Python code, as QSS for individual table cell backgrounds can be complex.
# This provides a clear visual cue in stock management.
STOCK_COLORS = {
    "out_of_stock": {
        "bg": QColor(
            COLORS["error_bg"]
        ),  # Light red background for out-of-stock items.
        "text": QColor(COLORS["error_dark"]),  # Dark red text.
        "border": QColor(
            COLORS["error"]
        ),  # Border color (if used for specific cell styling, e.g., programmatically).
    },
    "low_stock": {
        "bg": QColor(
            COLORS["warning_bg"]
        ),  # Light yellow/amber background for low stock.
        "text": QColor(COLORS["warning_dark"]),  # Dark yellow/amber text.
        "border": QColor(COLORS["warning"]),
    },
    "normal_stock": {
        "bg": QColor(
            COLORS["success_bg"]  # Light green background for normal stock.
        ),  # Or a more neutral color like COLORS['surface'] if less emphasis is needed.
        "text": QColor(
            COLORS["secondary_dark"]
        ),  # Dark green text. Or COLORS['text_primary'].
        "border": QColor(COLORS["success"]),  # Or COLORS['border'].
    },
    "overstocked": {  # A conceptual status, not explicitly used in the provided stock_view.py example, but good for planning.
        "bg": QColor(COLORS["info_bg"]),  # Light blue background for overstocked items.
        "text": QColor(COLORS["info_dark"]),  # Dark blue text.
        "border": QColor(COLORS["info"]),
    },
}

# --- Colors for Dashboard Widgets ---
# Specific colors assigned to different metrics/cards on the dashboard for visual distinction.
# This helps in quickly identifying different pieces of information.
DASHBOARD_COLORS = {
    "clients": COLORS["primary"],  # Color for the "Total Clients" card.
    "products": COLORS["secondary"],  # Color for the "Total Products" card.
    "sales": COLORS[
        "error"
    ],  # Color for "Total Sales" card (using error color for high visibility, or could be another accent).
    "low_stock": COLORS["warning"],  # Color for "Low Stock" items card.
    "revenue": COLORS["accent"],  # Example: for a total revenue card.
    "orders": COLORS["info"],  # Example: for an orders count card.
}

# --- Colors for Charts (e.g., pyqtgraph) ---
# A list of colors to be used cyclically in charts (e.g., for different lines in a line chart, or bars in a bar chart).
# A predefined sequence ensures visual consistency in data representation.
CHART_COLORS = [
    COLORS["primary"],
    COLORS["secondary"],
    COLORS["accent"],
    COLORS["warning"],
    COLORS["error"],
    COLORS[
        "info_dark"
    ],  # Using a defined dark variant for better contrast on light chart backgrounds or if lines overlap.
    "#f97316",  # Custom Orange (if not in main palette but needed for charts).
    "#84cc16",  # Custom Lime Green.
    "#ec4899",  # Custom Pink.
    COLORS["gray_500"],  # A gray from the palette, for less prominent series.
    COLORS["primary_light"],  # Lighter primary for variation.
    COLORS["secondary_light"],  # Lighter secondary.
]

# --- Colors for Semantic Status Badges/Tags ---
# General status indicators that can be used across different views (e.g., status of an order, user).
# Provides semantic meaning through color.
STATUS_COLORS = {
    "active": COLORS["secondary"],  # Green for active status.
    "inactive": COLORS["gray_500"],  # Gray for inactive.
    "pending": COLORS["warning"],  # Yellow/amber for pending.
    "processing": COLORS["info"],  # Blue for processing.
    "completed": COLORS["success"],  # Green for completed (alias for clarity).
    "cancelled": COLORS["error"],  # Red for cancelled.
    "draft": COLORS["gray_400"],  # Lighter gray for draft status.
    "archived": COLORS["gray_600"],  # Darker gray for archived items.
}


# --- Breakpoints (Conceptual) ---
# For responsive design concepts if adapting the UI for different window sizes programmatically.
# Qt Stylesheets do not directly support CSS-like media queries. Responsiveness in Qt is usually handled
# by layout managers (QGridLayout, QVBoxLayout, etc.) and programmatic adjustments.
# These values are for reference if manual responsive logic is implemented.
BREAKPOINTS = {
    "sm": 640,  # Small screen width (pixels).
    "md": 768,  # Medium screen width.
    "lg": 1024,  # Large screen width.
    "xl": 1280,  # Extra large screen width.
}

# --- Z-Index (Conceptual) ---
# For managing stacking order of overlapping widgets programmatically (e.g., using widget.raise_()).
# QSS does not have a direct 'z-index' property like CSS. Stacking order is generally
# determined by widget creation order or explicit calls to `raise_()` or `lower_()`.
# These values are for conceptual organization if manual stacking is managed.
Z_INDEX = {
    "dropdown": 1000,  # Dropdown lists should appear above most other elements.
    "modal": 2000,  # Modal dialogs should be on top of the application content.
    "tooltip": 3000,  # Tooltips appear above everything else.
    "notification": 4000,  # System-level notifications.
}


# --- Global Stylesheet Application ---
def apply_global_style(app):  # Function to apply styles to the QApplication instance.
    """
    Applies a global stylesheet to the QApplication instance and sets a default font.
    This function is called once at the beginning of the application (e.g., in main.py).
    Args:
        app (QApplication): The main application instance.
    """
    # Set a base style like "Fusion" for good cross-platform consistency before applying QSS.
    # Other options include "Windows", "Macintosh". Fusion is often recommended for custom styling.
    app.setStyle("Fusion")

    # Concatenate various style definitions from the STYLES dictionary to form a global stylesheet.
    # This applies common styles to many widgets by default.
    # More specific styles can be applied to individual widgets or containers as needed,
    # either by setting their `objectName` and using ID selectors in QSS (#objectName),
    # or by applying stylesheets directly to widget instances.
    global_stylesheet = (
        STYLES[
            "main_window"
        ]  # Style for the main application window background and default text.
        + STYLES[
            "input"
        ]  # General style for all input fields (QLineEdit, QComboBox, etc.).
        + STYLES["table"]  # General style for tables (QTableWidget).
        + STYLES["label"]  # General style for labels (QLabel).
        + STYLES["scrollbar"]  # Style for scrollbars.
        + STYLES["tooltip"]  # Style for tooltips.
        + STYLES[
            "sidebar_item"
        ]  # Style for QListWidget items, specifically for the sidebar.
        # It's often better to apply button styles more specifically where buttons are created
        # (e.g., in BaseView or individual views using `button.setStyleSheet(STYLES['button_primary'])`)
        # rather than globally, to avoid unintended styling of all QPushButtons.
        # However, they can be part of a base sheet if a very generic button look is desired for all buttons.
        # + STYLES["button_primary"]
        # + STYLES["button_secondary"]
        # Similarly for progress_bar and group_box, apply them where needed or make them more generic.
        # + STYLES["progress_bar"]
        # + STYLES["group_box"]
    )
    app.setStyleSheet(
        global_stylesheet
    )  # Apply the constructed global stylesheet to the application.

    # Set a default application font. This ensures consistent typography.
    default_font = QFont(
        FONTS["font_family"], FONTS["base"]
    )  # Use base size from the font scale.
    app.setFont(default_font)

    # Note on applying styles for a group project:
    # While a large global stylesheet is possible, it can sometimes lead to specificity issues
    # (where a style doesn't apply as expected due to conflicting rules) or make debugging styles harder.
    # A common and often more manageable approach is:
    # 1. Apply very general styles (like main window background, default font, default text color) globally, as done here.
    # 2. Apply common widget styles (like for all QLineEdits, all QTableWidgets) globally if they are highly consistent.
    # 3. For more complex or unique components (like a custom dashboard card, a specific dialog),
    #    apply their styles directly to them or their parent container. This can be done by:
    #    a. `widget.setStyleSheet(STYLES['my_specific_style'])` in the Python code.
    #    b. Using `objectName` for widgets and targeting them in QSS: `widget.setObjectName("myCard")`, then in QSS: `#myCard { ... }`.
    # This provides better encapsulation and makes it easier for different team members to work on styling their respective UI parts.
    # The `BaseView` class in this project is a good place to apply styles to common composite elements (like forms, CRUD buttons)
    # that are reused across multiple views, ensuring consistency for those shared patterns.
