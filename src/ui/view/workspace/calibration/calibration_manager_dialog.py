from PyQt5.QtWidgets import QComboBox, QDialog, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QFormLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from src.core.theme.tokens import UI_TAG

class CalibrationManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Calibration")
        self.setFixedSize(350, 420) 
        self.setProperty("class", UI_TAG.BG_ALERT)
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.lbl_preset = QLabel("Preset Name:")
        self.lbl_preset.setProperty("class", UI_TAG.TEXT_VIEW_SUBTITLE)
        

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Column_A_THF_2024")
        self.name_input.setProperty("class", UI_TAG.BG_INPUT)

        self.main_layout.addWidget(self.lbl_preset)
        self.main_layout.addWidget(self.name_input)


        self.lbl_fitType = QLabel("Fit Type:")
        self.lbl_fitType.setProperty("class", UI_TAG.TEXT_VIEW_SUBTITLE)

        self.main_layout.addWidget(self.lbl_fitType)

        self.fit_combo = QComboBox()
        items = ["Cubic (3rd Order)", "Quadratic (2nd Order)", "Linear (1st Order)"]
        self.fit_combo.addItems(items)
        self.fit_combo.setFixedHeight(30)
        self.fit_combo.setProperty("class", UI_TAG.BG_INPUT)

        self.main_layout.addWidget(self.fit_combo)

        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(10, 5, 10, 0)
        self.form_layout.setVerticalSpacing(10)
        self.form_layout.setLabelAlignment(Qt.AlignRight)

        double_validator = QDoubleValidator()

        self.input_a = QLineEdit()
        self.input_b = QLineEdit()
        self.input_c = QLineEdit()
        self.input_d = QLineEdit()
        
        labels_text = ["A (3rd):", "B (2nd):", "C (1st):", "D (0):"]
        inputs = [self.input_a, self.input_b, self.input_c, self.input_d]

        for text, inp in zip(labels_text, inputs):
            inp.setPlaceholderText("0.0")
            inp.setValidator(double_validator)
            inp.setAlignment(Qt.AlignRight)
            inp.setProperty("class", UI_TAG.BG_INPUT)
            
            lbl = QLabel(text)
            lbl.setProperty("class", UI_TAG.TEXT_VIEW_SUBTITLE)
            
            self.form_layout.addRow(lbl, inp)
        
        self.main_layout.addLayout(self.form_layout)

        self.main_layout.addStretch(1)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch(1) 

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("class", UI_TAG.BTN_SECONDARY)
        self.cancel_btn.setFixedSize(80, 32)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setProperty("class", UI_TAG.BTN_PRIMARY)
        self.save_btn.setFixedSize(80, 32)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.accept)
        
        self.btn_layout.addWidget(self.cancel_btn)
        self.btn_layout.addWidget(self.save_btn)
        
        self.main_layout.addLayout(self.btn_layout)

        self.fit_combo.currentIndexChanged.connect(self.update_visibility)
        self.update_visibility()

    def update_visibility(self):
        idx = self.fit_combo.currentIndex()
        self.input_a.setEnabled(idx == 0)
        self.input_b.setEnabled(idx <= 1)
        
    def get_data(self):
        def safe_float(text):
            stripped = text.strip()
            if not stripped:
                return 0.0
            try:
                return float(stripped.replace(',', ''))
            except ValueError:
                return 0.0

        return {
            "name": self.name_input.text() if self.name_input.text() else "Untitled",
            "fit_type": self.fit_combo.currentText(),
            "coeffs": [
                safe_float(self.input_a.text()),
                safe_float(self.input_b.text()),
                safe_float(self.input_c.text()),
                safe_float(self.input_d.text())
            ]
        }