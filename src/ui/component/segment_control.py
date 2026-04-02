from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup
from PyQt5.QtCore import pyqtSignal, QTimer
from src.util.create_svg_icon import create_svg_icon

class SegmentControl(QWidget):
    selectionChanged = pyqtSignal(str)

    def __init__(self, items: list, default_value: str, parent = None):
        super().__init__(parent)
        self.items = items
        self.buttons = {}
        self.setObjectName("customSegmentControl")

        self._pending_value = None
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(500)
        self._debounce_timer.timeout.connect(self._emit_selection)

        self._init_ui(default_value)

    def _init_ui(self, default_value):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        for i, (value, icon_info) in enumerate(self.items):
            btn = QPushButton()
            btn.setCheckable(True)
            
            btn.setProperty("svg_path", icon_info)
            btn.setProperty("value", value)          
            btn.setProperty("class", "segment-button") 
            
            if i == 0:
                btn.setProperty("position", "first")
            elif i == len(self.items) - 1:
                btn.setProperty("position", "last")
            else:
                btn.setProperty("position", "middle")

            self.button_group.addButton(btn)
            main_layout.addWidget(btn)
            self.buttons[value] = btn

        if default_value and default_value in self.buttons:
            self.buttons[default_value].setChecked(True)
            self._current_value = default_value
        elif self.items:
            first_value = self.items[0][0]
            self.buttons[self.items[0][0]].setChecked(True)
            self._current_value = first_value 

        self.button_group.buttonClicked.connect(self._on_button_clicked)

        


    def _refresh_icons(self, current_theme):
        new_color = current_theme["text_primary"]
        selected_color = current_theme["text_action"]

        for value, btn in self.buttons.items():
            svg_path = btn.property("svg_path")
            if svg_path:
                normal_icon = create_svg_icon(svg_path, new_color)
                selected_icon = create_svg_icon(svg_path, selected_color)
                
                btn.setProperty("icon_normal", normal_icon)
                btn.setProperty("icon_selected", selected_icon)

                if btn.isChecked():
                    btn.setIcon(selected_icon)
                else:
                    btn.setIcon(normal_icon)
    
    def _on_button_clicked(self, button):
        clicked_val = button.property("value")

        if clicked_val == self._current_value:
            return

        for val, btn in self.buttons.items():
            if btn == button:
                btn.setIcon(btn.property("icon_selected"))
            else:
                btn.setIcon(btn.property("icon_normal"))

        self._pending_value = clicked_val
        self._debounce_timer.start()
        
    def _emit_selection(self):
        if self._pending_value is not None:
            self._current_value = self._pending_value
            self.selectionChanged.emit(self._pending_value)

