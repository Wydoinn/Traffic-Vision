def get_stylesheet() -> str:
    """Returns the updated stylesheet for the application with brown and beige theme styling."""
    return """
        QMainWindow {
            background-color: #fcf7f1;
            border: none;
        }

        QLabel {
            color: #4a3c31;
            font-size: 12px;
            font-weight: 500;
        }

        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b08968, stop:1 #8b6b4e);
            color: #fcf7f1;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 12px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #c09978, stop:1 #9b7b5e);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a07958, stop:1 #7b5b3e);
        }
        QPushButton:disabled {
            background: #e8e2d9;
            color: #a89b8c;
        }

        QSpinBox, QDoubleSpinBox, QLineEdit {
            background-color: #fff9f2;
            color: #4a3c31;
            border: 2px solid #e8d5c5;
            border-radius: 8px;
            padding: 8px 12px;
            min-width: 30px;
            min-height: 15px;
            font-size: 12px;
            selection-background-color: #b08968;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            width: 20px;
            border: none;
            border-left: 1px solid #e8d5c5;
            background: #f5e6d8;
            border-top-right-radius: 8px;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            width: 20px;
            border: none;
            border-left: 1px solid #e8d5c5;
            background: #f5e6d8;
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

        QComboBox {
            background-color: #fff9f2;
            color: #4a3c31;
            border: 2px solid #e8d5c5;
            border-radius: 8px;
            padding: 8px 12px;
            min-width: 30px;
            min-height: 15px;
            font-size: 12px;
            selection-background-color: #b08968;
        }
        QComboBox::drop-down {
            border: none;
            border-left: 2px solid #e8d5c5;
            width: 30px;
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
            border: 2px solid #e8d5c5;
            selection-background-color: #b08968;
            selection-color: #fff9f2;
            background-color: #fff9f2;
            border-radius: 0px;
            padding: 5px;
        }

        QTabWidget::pane {
            background-color: #fff9f2;
            border: 2px solid #e8d5c5;
            border-radius: 8px;
            padding: 10px;
        }

        QTabBar::tab {
            background-color: #f5e6d8;
            color: #8b6b4e;
            padding: 12px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background-color: #fff9f2;
            color: #4a3c31;
            border-bottom: 2px solid #b08968;
        }
        QTabBar::tab:hover:!selected {
            color: #4a3c31;
            background-color: #faf0e6;
        }

        QGroupBox {
            border: 2px solid #e8d5c5;
            border-radius: 8px;
            margin-top: 10px;
            background-color: #fff9f2;
            color: #4a3c31;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 5px 10px;
            background-color: #fff9f2;
            color: #4a3c31;
            font-weight: bold;
            font-size: 14px;
        }

        QScrollArea {
            background-color: #fff9f2;
            border: none;
        }
        QScrollArea#videoDisplay, QScrollArea#heatmapDisplay {
            border: 2px solid #e8d5c5;
            border-radius: 8px;
        }
        QScrollArea > QWidget > QWidget {
            background-color: #fff9f2;
        }

        QScrollBar:vertical {
            background-color: #f5e6d8;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #b08968;
            border-radius: 5px;
            min-height: 20px;
            margin: 2px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        QMessageBox, QDialog {
            background-color: #fcf7f1;
            color: #4a3c31;
        }

        QTableWidget {
            background-color: #fff9f2;
            alternate-background-color: #faf0e6;
            color: #4a3c31;
            gridline-color: #e8d5c5;
            selection-background-color: #b08968;
            selection-color: #fff9f2;
            border: 2px solid #e8d5c5;
            border-radius: 8px;
        }
        QTableWidget::item {
            padding: 5px;
            border-bottom: 1px solid #e8d5c5;
        }

        QHeaderView::section {
            background-color: #f5e6d8;
            color: #4a3c31;
            padding: 5px;
            border: none;
            border-right: 1px solid #e8d5c5;
            border-bottom: 1px solid #e8d5c5;
            font-weight: bold;
        }

        QCheckBox {
            color: #4a3c31;
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #e8d5c5;
            border-radius: 4px;
            background-color: #fff9f2;
        }
        QCheckBox::indicator:checked {
            background-color: #b08968;
            border-color: #b08968;
            image: url(static/icons/checkmark.png);
        }
        QCheckBox::indicator:hover {
            border-color: #b08968;
        }

        QStatusBar {
            background-color: #fcf7f1;
            color: #4a3c31;
            border-top: 1px solid #e8d5c5;
        }
        
        QToolTip {
            background-color: #fff9f2;
            color: #4a3c31;
            border: 1px solid #e8d5c5;
            border-radius: 4px;
            padding: 5px;
        }
    """
