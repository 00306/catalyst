from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from src.ui.view.dialog.file_dialog import FileDialog
from src.core.theme.tokens import UI_TAG
from src.util.create_svg_icon import create_svg_icon
from src.core.theme.icons import SVG_ICONS

class DropZoneWidget(QFrame):
    sig_files_received = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.is_drag_active = False
        self.setProperty("svg_path", SVG_ICONS["folder"])
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; margin-bottom: 20px;")
        
        self.main_text = QLabel("Drag & Drop .D folders here")
        self.main_text.setProperty("class", UI_TAG.TEXT_PRIMARY)
        
        self.sub_text = QLabel("or click to browse")
        self.sub_text.setProperty("class", UI_TAG.TEXT_SECONDARY)
        
        layout.addStretch()
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.main_text, alignment=Qt.AlignCenter)
        layout.addWidget(self.sub_text, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.apply_style("normal")

    def apply_theme(self, current_theme):
        normal_color = current_theme["text_primary"]
        drag_color = current_theme["text_action"]
        
        svg_path = self.property("svg_path")
        
        if svg_path:
            normal_icon = create_svg_icon(svg_path, normal_color)
            drag_icon = create_svg_icon(svg_path, drag_color)
            
            self.setProperty("icon_normal", normal_icon)
            self.setProperty("icon_drag", drag_icon)
            
            self._refresh_icon()

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _refresh_icon(self):
        state_key = "icon_drag" if self.is_drag_active else "icon_normal"
        icon = self.property(state_key)
        
        if icon:
            self.icon_label.setPixmap(icon.pixmap(64, 64))

    def apply_style(self, state):
        self.setProperty("dropState", state)
        self._refresh_icon()

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_error_state(self):
        self.setStyleSheet("""
            DropZoneWidget {
                border: 2px dashed #FF6464; /* 경고 테두리 (TEXT_DANGER 색상) */
                border-radius: 8px;
                background-color: rgba(255, 100, 100, 0.05); /* 살짝 붉은 배경(옵션) */
            }
        """)

    def clear_error_state(self):
        self.setStyleSheet("")

    def enterEvent(self, event):
        if not self.is_drag_active:
            self.apply_style("hover")

    def leaveEvent(self, event):
        if not self.is_drag_active:
            self.apply_style("normal")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.is_drag_active = True
            self.apply_style("drag")
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.is_drag_active = False
        self.apply_style("normal")

    def dropEvent(self, event):
        self.is_drag_active = False
        self.apply_style("normal")
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.sig_files_received.emit(files)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.open_file_dialog()

    def open_file_dialog(self):
        dialog = FileDialog(
            parent=self, 
            title="Select Data Folders (.D)", 
            filter_str=".D Folders (*.D)", 
            mode="open_dir"
        )

        if dialog.exec_():
            paths = dialog.selectedFiles()
            if paths:
                self.sig_files_received.emit(paths)