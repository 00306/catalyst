import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.ui.MainWindow import MainWindow
from src.util.load_custom_fonts import load_custom_fonts
from PyQt5.QtGui import QFont, QFontDatabase
import ctypes


if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("catalyst.app")
    
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    font = QFont("Arial")
    font.setHintingPreference(QFont.PreferNoHinting)
    font.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
    app.setFont(font)

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
    window.setFocus()
    sys.exit(app.exec_())


