from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtCore import QByteArray, QSize, Qt
from PyQt5.QtSvg import QSvgRenderer


def create_svg_icon(svg_string: str, color_hex: str) -> QIcon:
    colored_svg = svg_string.replace('currentColor', color_hex)

    img_data = QByteArray(colored_svg.encode('utf-8'))

    renderer = QSvgRenderer(img_data)

    
    big_size = 128
    pixmap = QPixmap(big_size, big_size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)