import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.ui.MainWindow import MainWindow
from src.util.load_custom_fonts import load_custom_fonts

if __name__ == "__main__":
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    app.setStyle("windows")
    load_custom_fonts()

    custom_style = """
        * {
            outline: none;
        }
        QPushButton:focus, QListWidget:focus, QListWidget::item:focus {
            outline: none;
            border: none;
        }
    """
    
    app.setStyleSheet(custom_style)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


