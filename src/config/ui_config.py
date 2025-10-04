class UIConfig:
    """Configuration class for the User Interface.

    This class centralizes all the configuration parameters for the GUI,
    making it easy to theme and modify the visual aspects of the application.
    """
    # --- Project Info ---
    APP_WINDOW_TITLE = "BandaCV"
    UI_TITLE_LABEL = "BandaCV"

    # --- Color Palette ---
    COLOR_BACKGROUND = '#1e1e1e'
    COLOR_SURFACE = '#2d2d2d'
    COLOR_PRIMARY = '#00a2e8'
    COLOR_PRIMARY_HOVER = '#33b5eb'
    COLOR_PRIMARY_PRESSED = '#0077a8'
    COLOR_TEXT = '#e0e0e0'
    COLOR_TEXT_SECONDARY = '#a0a0a0'
    COLOR_DANGER = '#e53935'
    COLOR_SUCCESS = '#43a047'
    COLOR_BORDER = '#404040'

    # --- Font Settings ---
    FONT_FAMILY = "DejaVu Sans, Liberation Sans, sans-serif"

    # --- Window Settings ---
    DEFAULT_WINDOW_GEOMETRY = (100, 100, 1200, 800) # (x, y, width, height)

    # --- Base Stylesheets ---
    STYLESHEET_MAIN_WINDOW = f"""
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT};
        font-family: {FONT_FAMILY};
    """

    STYLESHEET_LABEL_TITLE = f"""
        font-size: 24px;
        font-weight: bold;
        color: {COLOR_TEXT};
    """

    STYLESHEET_LABEL_SUBTITLE = f"""
        font-size: 16px;
        font-weight: bold;
        color: {COLOR_TEXT};
    """

    STYLESHEET_LABEL_BODY = f"""
        font-size: 12px;
        color: {COLOR_TEXT_SECONDARY};
    """

    STYLESHEET_PUSHBUTTON = f"""
        QPushButton {{
            background-color: {COLOR_SURFACE};
            color: {COLOR_TEXT};
            border: 1px solid {COLOR_BORDER};
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_PRIMARY_HOVER};
            color: {COLOR_BACKGROUND};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_PRIMARY_PRESSED};
        }}
    """
    
    STYLESHEET_CHECKBOX = f"""
        QCheckBox {{
            spacing: 5px;
            color: {COLOR_TEXT};
            font-size: 12px;
        }}
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border: 1px solid {COLOR_BORDER};
            border-radius: 3px;
            background-color: {COLOR_SURFACE};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLOR_PRIMARY};
        }}
    """

    STYLESHEET_SLIDER = f"""
        QSlider::groove:horizontal {{
            border: 1px solid {COLOR_BORDER};
            height: 4px;
            background: {COLOR_SURFACE};
            margin: 2px 0;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {COLOR_PRIMARY};
            border: 1px solid {COLOR_PRIMARY};
            width: 16px;
            height: 16px;
            margin: -7px 0;
            border-radius: 8px;
        }}
    """

    STYLESHEET_LINEEDIT = f"""
        background-color: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 5px;
        color: {COLOR_TEXT};
    """

    # --- Widget Specific Settings ---
    UI_PWM_INPUT_WIDTH = 50
    PWM_SLIDER_PAGE_STEP = 20
    UI_LED_SIZE = (32, 32)
    UI_LED_ON_STYLE = f"background-color: {COLOR_DANGER}; border-radius: 16px;"
    UI_LED_OFF_STYLE = f"background-color: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 16px;"
    UI_WEBCAM_BORDER_STYLE = f"border: 1px solid {COLOR_BORDER};"

    # --- Graph Settings ---
    GRAPH_RPM_MAX_LIMIT = 300
    GRAPH_FIGSIZE = (5.3, 2.2)
    GRAPH_FACE_COLOR = COLOR_BACKGROUND
    GRAPH_TICK_COLOR = COLOR_TEXT_SECONDARY
    GRAPH_SPINE_COLOR = COLOR_BORDER
    GRAPH_LINE_COLOR = COLOR_PRIMARY
    GRAPH_LINE_WIDTH = 2
    GRAPH_LINE_STYLE = 'solid'
    GRAPH_TITLE = 'REAL-TIME RPM READING'
    GRAPH_TITLE_FONT = {
        'color': COLOR_TEXT,
        'fontweight': 'bold',
        'fontsize': 12,
    }
    GRAPH_X_LABEL = 'time (s)'
    GRAPH_Y_LABEL = 'velocity (rpm)'
    GRAPH_SMOOTHING_WINDOW = 5

    # --- Servo Debug Dialog ---
    SERVO_DEBUG_WINDOW_TITLE = "Servo Debugging"
    SERVO_DEBUG_BTN_TRIANGLE = "Triangle / Red / Small (Pos: 30°)"
    SERVO_DEBUG_BTN_SQUARE = "Square / Yellow / Medium (Pos: 90°)"
    SERVO_DEBUG_BTN_CIRCLE = "Circle / Green / Large (Pos: 150°)"
    SERVO_DEBUG_BTN_UNKNOWN = "Unknown / Home (Pos: 0°)"