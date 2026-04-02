from PyQt5.QtWidgets import QComboBox, QLineEdit, QFormLayout, QHBoxLayout, QSizePolicy, QDialog, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from src.ui.component.base_card import BaseCard
from src.model.calibration_data import CalibrationData
from ..mwd.mini_curve_widget import MiniCurveWidget
from .calibration_manager_dialog import CalibrationManagerDialog
from src.config.app_config import AppConfig
from src.core.theme.tokens import UI_TAG
from src.ui.view.dialog.confirm_dialog import ConfirmDialog

class CalibrationCard(BaseCard):
    sig_calibration_changed = pyqtSignal(object)

    def __init__(self):
        super().__init__(title="Calibration Curve")
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        
        self._apply_styles()
        self._init_ui()
        self.setup_connections()
        self.refresh_preset_combo() 
        self.emit_calibration_data()

    def _apply_styles(self):
        if hasattr(self, 'title_label'):
            self.title_label.setProperty("class", UI_TAG.TEXT_ACCENT)

        
        self.setProperty("class", UI_TAG.BG_CARD_SECONDARY)

    def _init_ui(self):
        self.preset_combo = QComboBox()
        self.preset_combo.setProperty("class", UI_TAG.BG_INPUT)
        self.header_layout.addWidget(self.preset_combo)
        
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedWidth(30)
        self.add_btn.setFixedHeight(26)
        self.add_btn.setProperty("class", UI_TAG.BTN_PANEL_ADD)
        self.header_layout.addWidget(self.add_btn)

        self.del_btn = QPushButton("-")
        self.del_btn.setFixedWidth(30)
        self.del_btn.setFixedHeight(26)
        
        self.del_btn.setProperty("class", UI_TAG.BTN_PANEL_ADD)
        self.header_layout.addWidget(self.del_btn)

        # --- 2. Main Container (HBox) ---
        self.h_container = QHBoxLayout()
        self.h_container.setSpacing(30)
        self.h_container.setContentsMargins(5, 15, 20, 5)

        self.form_layout = QFormLayout()
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.form_layout.setVerticalSpacing(10)

        field_width = 120 
        
        def create_readonly_input():
            line_edit = QLineEdit()
            line_edit.setReadOnly(True)
            line_edit.setFixedWidth(field_width)
            line_edit.setAlignment(Qt.AlignRight)
            line_edit.setProperty("class", UI_TAG.BG_INPUT)
            return line_edit

        self.input_a = create_readonly_input()
        self.input_b = create_readonly_input()
        self.input_c = create_readonly_input()
        self.input_d = create_readonly_input()

        lbl_input_a = QLabel("A (3rd):")
        lbl_input_b = QLabel("B (2nd):")
        lbl_input_c = QLabel("C (1st):")
        lbl_input_d = QLabel("D (0):")

        lbl_input_a.setProperty("class", UI_TAG.TEXT_SECONDARY)
        lbl_input_b.setProperty("class", UI_TAG.TEXT_SECONDARY)
        lbl_input_c.setProperty("class", UI_TAG.TEXT_SECONDARY)
        lbl_input_d.setProperty("class", UI_TAG.TEXT_SECONDARY)

        self.form_layout.addRow(lbl_input_a, self.input_a)
        self.form_layout.addRow(lbl_input_b, self.input_b)
        self.form_layout.addRow(lbl_input_c, self.input_c)
        self.form_layout.addRow(lbl_input_d, self.input_d)

        self.h_container.addLayout(self.form_layout)

        self.mini_curve = MiniCurveWidget()
        self.mini_curve.setFixedSize(160, 160)
        self.mini_curve.setProperty("class", UI_TAG.BG_GRAPH_AREA)
        self.h_container.addWidget(self.mini_curve, 0, Qt.AlignTop)

        self.h_container.addStretch(1)
        self.content_layout.addLayout(self.h_container)

    def setup_connections(self):
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        self.add_btn.clicked.connect(self.open_calibration_manager)
        self.del_btn.clicked.connect(self.delete_current_preset)

    def delete_current_preset(self):
        target = self.preset_combo.currentText()
        if not target or target == "No Presets Found":
            return
            
        dialog = ConfirmDialog(self, title="Delete Preset", message=f"Are you sure you want to delete\n'{target}'?")
        
        if dialog.exec_() == QDialog.Accepted:
            AppConfig.delete_calibration_preset(target)
            self.refresh_preset_combo()

            
    def on_preset_changed(self, text):
        if not text or text == "No Presets Found":
            return
            
        presets = AppConfig.get_calibration_presets()
        if text not in presets:
            return
    
        data = presets[text]
        coeffs = data.get('coeffs', [0.0, 0.0, 0.0, 0.0])

        self.input_a.setText(f"{coeffs[0]:.4e}")
        self.input_b.setText(f"{coeffs[1]:.4e}")
        self.input_c.setText(f"{coeffs[2]:.4e}")
        self.input_d.setText(f"{coeffs[3]:.4e}")

        self.emit_calibration_data()

    def open_calibration_manager(self):
        dialog = CalibrationManagerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            name = data.pop('name')
            AppConfig.save_calibration_preset(name, data)
            self.refresh_preset_combo()
            self.preset_combo.setCurrentText(name)

    def refresh_preset_combo(self):
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        
        presets = AppConfig.get_calibration_presets()

        if not presets:
            self.preset_combo.addItem("No Presets Found")
            self.preset_combo.blockSignals(False)
            return
        
        self.preset_combo.addItems(list(presets.keys()))
        self.preset_combo.blockSignals(False)
        
        self.on_preset_changed(self.preset_combo.currentText())

    def emit_calibration_data(self):
        def get_val(line_edit):
            text = line_edit.text()
            return float(text) if text else 0.0

        A = get_val(self.input_a) if self.input_a.isVisible() else 0.0
        B = get_val(self.input_b) if self.input_b.isVisible() else 0.0
        C = get_val(self.input_c)
        D = get_val(self.input_d)

        self.mini_curve.update_coefficients(A, B, C, D)

        data_obj = CalibrationData(
            fit_type=self.preset_combo.currentText(),
            A=A, B=B, C=C, D=D
        )
        self.sig_calibration_changed.emit(data_obj)

    def get_coefficients(self):
        try:
            return [
                float(self.input_a.text() or 0),
                float(self.input_b.text() or 0),
                float(self.input_c.text() or 0),
                float(self.input_d.text() or 0)
            ]
        except ValueError:
            return [0.0, 0.0, 0.0, 0.0]