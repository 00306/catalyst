from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QCheckBox
from PyQt5.QtCore import pyqtSignal
from src.ui.view.workspace.calibration.calibration_card import CalibrationCard
from src.model.calibration_data import CalibrationData
from src.model.project_config import ProjectMetadata
from .chromatogram.chromatogram_widget import ChromatogramWidget
from .mwd.mwd_chart_widget import MWDChartWidget
from .mwd.summary_table_widget import SummaryTableWidget
from src.core.theme.tokens import UI_TAG

class ControlPanelWidget(QWidget):
    sig_apply_range = pyqtSignal(float, float)
    sig_save_meta = pyqtSignal(dict)
    sig_calibration_updated = pyqtSignal(object)
    sig_range_requested = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.meta_fields = {}
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 15, 0, 0)

        self.chroma_view = ChromatogramWidget()
        self.chroma_view.setMinimumHeight(400)
        self.content_layout.addWidget(self.chroma_view, 1)

        self.chk_apply_all = QCheckBox("Apply to All (Global Range)")
        self.chk_apply_all.setChecked(True)
        self.chk_apply_all.setProperty("class", UI_TAG.TEXT_SECONDARY)
        self.chk_apply_all.clicked.connect(self.handle_apply_range)

        self.chk_layout = QHBoxLayout()
        self.chk_layout.addStretch()
        self.chk_layout.addWidget(self.chk_apply_all)
        self.chk_layout.setContentsMargins(0, 5, 5, 5)

        self.content_layout.addLayout(self.chk_layout)

        self.analysis_layout = QHBoxLayout(self)
        self.analysis_layout.setContentsMargins(0, 0, 0, 15)

        self.cal_card = CalibrationCard()
        self.analysis_layout.addWidget(self.cal_card, 1)

        self.mwd_chart = MWDChartWidget()
        self.mwd_chart.setMinimumHeight(400)
        self.analysis_layout.addWidget(self.mwd_chart, 4)

        self.summary_table = SummaryTableWidget()
        
        self.content_layout.addLayout(self.analysis_layout)
        self.content_layout.addWidget(self.summary_table)

        self.content_layout.addStretch() 

        self.main_layout.addWidget(self.content_widget)

    def apply_theme(self, current_theme, current_graph_theme):
        self.chroma_view.on_theme_changed(current_graph_theme)
        self.mwd_chart.on_theme_changed(current_theme, current_graph_theme)

    def draw_chromatogram(self, signals, color_map, current_graph_theme, selected_idx):
        self.chroma_view.update_plot(signals, color_map, current_graph_theme, selected_idx)

    def handle_apply_range(self, state):
        self.sig_range_requested.emit(state)

    def update_table(self, results):
        self.summary_table.update_table(results)

    def setup_connections(self):
        self.cal_card.sig_calibration_changed.connect(self.handle_calibration_change)
        self.chroma_view.slice_changed_signal.connect(self.sig_apply_range.emit)

    def handle_calibration_change(self, cal_data: CalibrationData):
        self.sig_calibration_updated.emit(cal_data)

    def update_mwd_chart(self, mwd_data_list, selected_idx, color_map):
        self.mwd_chart.update_mwd_chart(mwd_data_list, selected_idx, color_map)

    def sync_ui_update(self, is_apply_all, current_sample_name):
        should_lock = (not is_apply_all) and (current_sample_name is None)
        self.chroma_view.set_bar_lock(should_lock)

    def set_metadata(self, metadata: ProjectMetadata):
        while self.meta_layout.count():
            item = self.meta_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.meta_fields.clear()

        keys_to_show = ["project_name", "sample_names", "channel_name", "z_unit"]

        for key in keys_to_show:
            val = getattr(metadata, key, "")
            line_edit = QLineEdit()
            line_edit.editingFinished.connect(self.on_save_meta)
            
            if isinstance(val, list):
                clean_list = [str(v) for v in val if str(v).strip()]
                line_edit.setText(", ".join(clean_list))
            else:
                line_edit.setText(str(val))
                
            display_label = key.replace("_", " ").title()
            self.meta_layout.addRow(display_label + ":", line_edit)
            
            self.meta_fields[key] = line_edit

    def on_apply_range(self):
        self.sig_apply_range.emit(self.spin_start.value(), self.spin_end.value())

    def on_save_meta(self):
        updated_meta = {}
        for key, widget in self.meta_fields.items():
            val = widget.text()

            if key == "sample_names":
                updated_meta[key] = [s.strip() for s in val.split(",") if s.strip()]
            else:
                updated_meta[key] = val
        
        self.sig_save_meta.emit(updated_meta)

