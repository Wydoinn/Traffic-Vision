from PyQt6.QtWidgets import QPushButton

def get_stylesheet(is_dark_theme: bool) -> str:
    """Returns the stylesheet for the application, adapting to system theme."""
    if is_dark_theme:
        return get_dark_stylesheet()
    else:
        return get_light_stylesheet()

def is_system_dark_theme() -> bool:
    """Detects if the system is using a dark theme."""
    test_button = QPushButton()
    bg_color = test_button.palette().color(test_button.backgroundRole())
    return bg_color.lightnessF() < 0.5

def get_dark_stylesheet() -> str:
    """Returns the dark theme stylesheet."""
    return """
        QMainWindow {
            background-color: #1a1a1a;
            color: #f0f0f0;
            border: none;
        }
        QLabel {
            color: #f0f0f0;
            font-size: 12px;
            font-weight: 500;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6B8CEF, stop:1 #8E54E9);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 12px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7B9CFF, stop:1 #9E64F9);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5B7CDF, stop:1 #7E44D9);
        }
        QPushButton:disabled {
            background: #444444;
            color: #888888;
        }
        QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox {
            background-color: #222222;
            color: #f0f0f0;
            border: 3px solid #444444;
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 30px;
            min-height: 15px;
            font-size: 12px;
            selection-background-color: #6B8CEF;
            selection-color: #ffffff;
        }
        QTabWidget::pane {
            background-color: #1a1a1a;
            border: 1px solid #444444;
            border-radius: 10px;
            padding: 10px;
        }
        QTabBar::tab {
            background-color: #222222;
            color: #bbbbbb;
            padding: 12px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background-color: #1a1a1a;
            color: #f0f0f0;
            border-bottom: 2px solid #6B8CEF;
        }
        QTabBar::tab:hover:!selected {
            color: #f0f0f0;
            background-color: #333333;
        }
        QGroupBox {
            border: 4px solid #444444;
            border-radius: 8px;
            margin-top: 10px;
            background-color: #1a1a1a;
            color: #f0f0f0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 5px 10px 0 10px;
            background-color: #1a1a1a;
            color: #f0f0f0;
            font-weight: bold;
            font-size: 14px;
        }
        QScrollArea {
            background-color: #1a1a1a;
            border: none;
            color: #f0f0f0;
        }
        QScrollArea#videoDisplay, QScrollArea#heatmapDisplay {
            border: 4px solid #444444;
            border-radius: 8px;
        }
        QScrollArea > QWidget > QWidget {
            background-color: #1a1a1a;
        }
        QScrollBar:vertical {
            background-color: #222222;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #666666;
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """

def get_light_stylesheet() -> str:
    """Returns the light theme stylesheet."""
    return """
        QMainWindow {
            background-color: #fcfaf8;
            border: none;
        }
        QLabel {
            color: #4a3c31;
            font-size: 12px;
            font-weight: 500;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6B8CEF, stop:1 #8E54E9);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 12px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7B9CFF, stop:1 #9E64F9);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5B7CDF, stop:1 #7E44D9);
        }
        QPushButton:disabled {
            background: #e8e2d9;
            color: #a89b8c;
        }
        QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox {
            background-color: #f8f6f4;
            color: #4a3c31;
            border: 3px solid #f0ece8;
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 30px;
            min-height: 15px;
            font-size: 12px;
            selection-background-color: #6B8CEF;
        }
        QTabWidget::pane {
            background-color: #faf6f1;
            border: 1px solid #e8e2d9;
            border-radius: 10px;
            padding: 10px;
        }
        QTabBar::tab {
            background-color: #f5f1ea;
            color: #8c7b6b;
            padding: 12px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background-color: #faf6f1;
            color: #4a3c31;
            border-bottom: 2px solid #6B8CEF;
        }
        QTabBar::tab:hover:!selected {
            color: #4a3c31;
            background-color: #f4f2f0;
        }
        QGroupBox {
            border: 4px solid #e8e2d9;
            border-radius: 8px;
            margin-top: 10px;
            background-color: #faf6f1;
            color: #4a3c31;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 5px 10px 0 10px;
            background-color: #faf6f1;
            color: #4a3c31;
            font-weight: bold;
            font-size: 14px;
        }
        QScrollArea {
            background-color: #faf6f1;
            border: none;
        }
        QScrollArea#videoDisplay, QScrollArea#heatmapDisplay {
            border: 4px solid #e8e2d9;
            border-radius: 8px;
        }
        QScrollArea > QWidget > QWidget {
            background-color: #faf6f1;
        }
        QScrollBar:vertical {
            background-color: #f5f1ea;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #d4cbc1;
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """
