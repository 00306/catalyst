from src.util.resource_path import resource_path
from PyQt5.QtGui import QFontDatabase

def load_custom_fonts():
    font_files = [
        "asset/font/Arimo-Regular.ttf",
    ]
    
    for relative_path in font_files:
        font_path = resource_path(relative_path)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)