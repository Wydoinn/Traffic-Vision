def get_stylesheet() -> str:
    """Returns the updated stylesheet for the application with QComboBox arrow styling."""
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
        QSpinBox, QDoubleSpinBox, QLineEdit {
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
        QComboBox {
            background-color: #f8f6f4;
            color: #4a3c31;
            border: 3px solid #f0ece8;
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 30px;
            min-height: 15px;
            font-size: 12px;
            selection-background-color: #6B8CEF;
            padding-right: 30px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left: 1px solid #e8e2d9;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
        }
        QComboBox::down-arrow {
            image: url(static/icons/down_arrow.png);
            width: 10px;
            height: 10px;
        }
        QComboBox:on {
            border-bottom-right-radius: 0px;
            border-bottom-left-radius: 0px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #e8e2d9;
            selection-background-color: #6B8CEF;
            selection-color: white;
            background-color: #f8f6f4;
            border-radius: 0px;
            padding: 5px;
            outline: none;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #f8f6f4;
            color: #4a3c31;
            border: 3px solid #f0ece8;
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 80px;
            min-height: 15px;
            font-size: 12px;
            selection-background-color: #6B8CEF;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            width: 20px;
            border: none;
            border-left: 1px solid #e8e2d9;
            background: #f5f1ea;
            border-top-right-radius: 8px;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            width: 20px;
            border: none;
            border-left: 1px solid #e8e2d9;
            background: #f5f1ea;
            border-bottom-right-radius: 8px;
        }
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            image: url(static/icons/up_arrow.png);
            width: 10px;
            height: 10px;
        }
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            image: url(static/icons/down_arrow.png);
            width: 10px;
            height: 10px;
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
