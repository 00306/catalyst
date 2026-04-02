from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QHBoxLayout, QFrame, QApplication, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from .graph_widget import GraphWidget
from .control_panel_widget import ControlPanelWidget
from src.ui.state.plot_state import PlotState
from src.model.gpc_data_set import Signal, AnalysisResult
from src.core.cos2d_engine import COS2DEngine
from src.core.gpc_engine import GPCEngine
from src.util.color_provider import ColorProvider
import numpy as np
from src.core.theme.tokens import UI_TAG
from src.core.theme.icons import SVG_ICONS
from src.ui.component.segment_control import SegmentControl
from src.core.theme.theme_manager import ThemeManager

class ProjectView(QWidget):
    sig_metadata_changed = pyqtSignal(dict)
    sig_single_line_graph_cilcked = pyqtSignal(str)
    sig_project_data_changed = pyqtSignal()

    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset
        self.metadata = self.dataset.metadata
        self.is_loading = True
        self._is_theme_dirty = False

        self.setProperty("class", UI_TAG.BG_BASE)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.theme_manager = ThemeManager()
        self.theme = self.theme_manager.get_resolved_theme()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        self.color_provider = ColorProvider()

        self.current_calibration = None

        self._init_ui()

    def _init_ui(self):

        scroll_content_widget = QWidget()
        scroll_content_widget.setContentsMargins(10, 0, 10, 0)
        
        main_layout = QVBoxLayout(scroll_content_widget) 
        
        main_layout.setSpacing(0)
        
        self.plot_state = PlotState()
        self.graph_widget = GraphWidget()
        self.graph_widget.setMinimumHeight(600)
        self.control_panel_widget = ControlPanelWidget()
        self.header_widget = self._create_header_widget()
        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.graph_widget)
        main_layout.addWidget(self.control_panel_widget)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content_widget)
        

        scroll_area.setObjectName("transparent_scroll_area")
        scroll_area.viewport().setObjectName("transparent_viewport")
        scroll_content_widget.setObjectName("transparent_content_widget")
        scroll_area.setAttribute(Qt.WA_StyledBackground, True)
        scroll_area.setProperty("class", f"{UI_TAG.BG_BASE} {UI_TAG.TEXT_PRIMARY}")
        
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll_area)

        self.graph_widget.sig_clicked_sample.connect(self.handle_line_graph_clicked)
        self.control_panel_widget.sig_apply_range.connect(self.handle_range_apply)

        self.control_panel_widget.sig_save_meta.connect(self.sig_metadata_changed)
        self.control_panel_widget.sig_calibration_updated.connect(self.handle_calibration_change)
        self.control_panel_widget.sig_range_requested.connect(self.on_apply_range_toggled)

        self.plot_state.sig_analysis_range_changed.connect(self._handle_range_changed)
        self.plot_state.sig_changed.connect(
            lambda *args: QTimer.singleShot(500, self._refresh_graph)
        )

        self.view_mode_selector._refresh_icons(self.theme)
        self.graph_widget.sig_render_finish.connect(lambda: self.set_loading(False))

    def on_theme_changed(self):
        if self.isVisible():
            self.apply_theme()
        else:
            self._is_theme_dirty = True
    

    def on_apply_range_toggled(self, state):
        is_checked = state
        self.plot_state.set_apply_to_all(is_checked)

        self._update_all_views()

    def apply_theme(self):
        current_theme = self.theme_manager.get_resolved_theme()
        current_graph_theme = self.theme_manager.get_graph_theme()

        self.graph_widget.apply_theme(current_theme, current_graph_theme)
        self.control_panel_widget.apply_theme(current_theme, current_graph_theme)
        self.view_mode_selector._refresh_icons(current_theme)

    def _handle_range_changed(self, target_name, start_t, end_t):
        if not self.current_calibration:
            return
        
        if target_name == "ALL":
            for name in self.metadata.sample_names:
                self._calculate_single_sample(name, start_t, end_t, update_ui=False)
            
            self._calculate_2d_cos(start_t, end_t)
            self._update_all_views()

        else:
            self._calculate_single_sample(target_name, start_t, end_t, update_ui=True)
    
    def _handle_cos_changed(self):
        self.graph_widget.update_contour_graph(self.plot_state, self.metadata)

    def handle_calibration_change(self, cal_data):
        self.current_calibration = cal_data
        max_t = float(self.plot_state.full_X[0].max())
        self._calculate_all_samples(0, max_t)

    def _calculate_all_samples(self, start_t, end_t):
        if not self.current_calibration:
            return
            
        for sample_name in self.metadata.sample_names:
            if sample_name not in self.plot_state.integration_ranges:
                self.plot_state.integration_ranges[sample_name] = (start_t, end_t)
            
            self._calculate_single_sample(sample_name, update_ui=False)

        self._update_all_views()

    def _calculate_single_sample(self, target_name: str, start_t: float = None, end_t: float = None, update_ui: bool = True):
        if not self.current_calibration or not target_name:
            return

        if start_t is None or end_t is None:
            start_t, end_t = self.plot_state.integration_ranges.get(target_name, (None, None))
            
        if start_t is None or end_t is None:
            return

        try:
            target_idx = self.metadata.sample_names.index(target_name)
        except ValueError:
            return

        raw_X = self.plot_state.full_X[0] 
        raw_Z = self.plot_state.full_Z[target_idx]
        mask = (raw_X >= start_t) & (raw_X <= end_t)
        sliced_time = raw_X[mask]
        sliced_intensity = raw_Z[mask]

        if len(sliced_time) < 2:
            return

        coeffs = [self.current_calibration.A, self.current_calibration.B, self.current_calibration.C, self.current_calibration.D]
        
        engine = GPCEngine(coeffs)
        result = engine.process_and_calculate(sliced_time, sliced_intensity)

        if result is None:
            analysis_obj = AnalysisResult(
                mn=0.0,
                mw=0.0,
                pdi=0.0,
                start_time=start_t,
                end_time=end_t,
                log_mw_axis=np.array([]),
                mwd_signal=np.array([])
            )

        else:
            analysis_obj = AnalysisResult(
                mn=result['Mn'],
                mw=result['Mw'],
                pdi=result['PDI'],
                start_time=start_t,
                end_time=end_t,
                log_mw_axis=result['log_mw_axis'],
                mwd_signal=result['mwd_signal']
            )
        
        self.dataset.results[target_name] = analysis_obj

        if update_ui:
            self._update_all_views()


    def _calculate_2d_cos(self, start_t, end_t):
        if self.plot_state.full_Z is None: return
        
        raw_X = self.plot_state.full_X[0]

        indices = np.where((raw_X >= start_t) & (raw_X <= end_t))[0]
        if len(indices) == 0: return
        
        pad = 10
        start_idx = max(0, indices[0] - pad)
        end_idx = min(len(raw_X) - 1, indices[-1] + pad)
        
        sliced_time = raw_X[start_idx : end_idx + 1]
        matrix_Z = np.array([z[start_idx : end_idx + 1] for z in self.plot_state.full_Z])

        cos_results = COS2DEngine.process(matrix_Z, calc_sync=True, calc_async=True)
        

        self.plot_state.update_cos_data(
            time_axis=sliced_time,
            avg_Z=cos_results['avg_Z'],
            sync_Z=cos_results.get('sync_Z'),
            async_Z=cos_results.get('async_Z')
            )

    def _start_rendering(self):
        self.set_loading(True)

        self.graph_widget.update_graph(self.plot_state)

    def handle_line_graph_clicked(self, name):
        self.plot_state.set_active_sample(name)
        self._update_all_views()
        
    def set_loading(self, loading: bool):
        self.is_loading = loading

    def update_data(self, X, Y, Z):
        self.set_loading(True)
        self.plot_state.load_initial_data(X, Y, Z, self.metadata.sample_names)
        self.color_provider.generate_color_map(self.metadata.sample_names)
        self.control_panel_widget.cal_card.emit_calibration_data()

        if self.current_calibration:
            max_t = float(self.plot_state.full_X[0].max())
            self._calculate_all_samples(0, max_t)
        
        self._calculate_2d_cos(0, max_t)

        self.graph_widget.load_plot_data(
            self.plot_state, 
            self.metadata, 
            self.color_provider.get_color_map(),
            self.theme_manager.get_resolved_theme(),
            self.theme_manager.get_graph_theme()
        )

        try:
            self.plot_state.sig_cos_updated.disconnect()
        except TypeError:
            pass
            
        self.plot_state.sig_cos_updated.connect(
            lambda: self.graph_widget.update_cos_data_only(
                self.plot_state.cos_time_axis,
                self.plot_state.cos_sync_Z,
                self.plot_state.cos_async_Z,
                self.plot_state.avg_Z
            )
        )

        self._update_all_views()

    def _render_2d_overlay(self):
        if self.plot_state.full_X is None or len(self.plot_state.full_X) == 0:
            return
        if self.plot_state.full_Z is None or len(self.plot_state.full_Z) == 0:
            return

        target_name = self.plot_state.current_sample_name
        selected_idx = None
        signals = []

        det_name = self.metadata.default_detector
        unit = self.metadata.z_unit_dict.get(det_name, "")
        raw_X = self.plot_state.full_X[0]


        for i, sample_name in enumerate(self.metadata.sample_names):
            raw_Z = self.plot_state.full_Z[i]

            method = self.metadata.methods.get(sample_name, "Unknown")
            date = self.metadata.analysis_dates.get(sample_name, "Unknown")
            instrument = self.metadata.instruments.get(sample_name, "Unknown")

            sig = Signal(
                sample_name=sample_name,
                detector_name=det_name,
                time=raw_X,
                intensity=raw_Z,
                unit=unit,
                method=method,
                date=date,
                instrument=instrument
            )
                
            signals.append(sig)
            
            if target_name == sample_name:
                selected_idx = i

        color_map = self.color_provider.get_color_map()
        current_graph_theme = self.theme_manager.get_graph_theme()
        self.control_panel_widget.draw_chromatogram(signals, color_map, current_graph_theme, selected_idx)

    def handle_view_mode_change(self, mode):
        self.theme = self.theme_manager.get_resolved_theme()
        self.graph_widget.set_loading(True, self.theme)
        QApplication.processEvents()

        self.plot_state.set_view_mode(mode)

    def handle_range_apply(self, start_t, end_t):
        self.set_loading(True)
        self.plot_state.update_analysis_range(start_t, end_t)

    def _refresh_graph(self):
        color_map = self.color_provider.get_color_map()
        if self.metadata.mode == "Multi-Detector":
            self.graph_widget.update_multi_graph(self.plot_state, self.metadata)
        else:
            self.graph_widget.load_plot_data(self.plot_state, self.metadata, color_map, self.theme_manager.get_resolved_theme(), self.theme_manager.get_graph_theme())

    def _render_mwd_overlay(self):
        if not self.dataset.results:
            return

        target_name = self.plot_state.current_sample_name
        selected_idx = None
        mwd_data_list = []

        for i, sample_name in enumerate(self.metadata.sample_names):
            if target_name == sample_name:
                selected_idx = i

            if sample_name in self.dataset.results:
                result = self.dataset.results[sample_name]
                mwd_data_list.append({
                    "name": sample_name,
                    "x": result.log_mw_axis,
                    "y": result.mwd_signal
                })
            else:
                mwd_data_list.append(None)

        color_map = self.color_provider.get_color_map()
        self.control_panel_widget.update_mwd_chart(mwd_data_list, selected_idx, color_map)

    def _update_all_views(self):
        self.control_panel_widget.update_table(self.dataset.results)
        self._render_2d_overlay()
        self._render_mwd_overlay()
        self.control_panel_widget.sync_ui_update(is_apply_all=self.plot_state.apply_to_all,
                                                 current_sample_name=self.plot_state.current_sample_name)
        

    def _create_header_widget(self):
        header_widget = QWidget()
        layout = QVBoxLayout(header_widget)
        layout.setContentsMargins(0, 20, 20, 10) 
        layout.setSpacing(15)

        title_layout = QHBoxLayout()
        
        title_label = QLabel("DATA DASHBOARD")
        title_label.setProperty("class", UI_TAG.TEXT_VIEW_TITLE)
        
        project_name = getattr(self.metadata, 'project_name', 'Unknown Project')
        subtitle_label = QLabel(f"Selected Project: {project_name}")
        subtitle_label.setWordWrap(True)
        subtitle_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        subtitle_label.setMinimumWidth(500)
        subtitle_label.setProperty("class", UI_TAG.TEXT_VIEW_SUBTITLE)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        title_layout.addStretch()
 
        description = getattr(self.metadata, 'description', 'No Description')
        desc_lbl = QLabel(description)
        desc_lbl.setProperty("class", UI_TAG.BG_QUOTE)
        desc_lbl.setWordWrap(True)
        desc_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        desc_lbl.setMinimumWidth(500)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        det_name = self.metadata.default_detector
        det_card = self._create_info_card("Detector:", det_name)
        
        sample_count = str(len(self.metadata.sample_names))
        count_card = self._create_info_card("Sample Count:", sample_count)
        
        cards_layout.addWidget(det_card)
        cards_layout.addWidget(count_card)
        cards_layout.addStretch()
        
        svg_text_line = SVG_ICONS["chart_line"]
        svg_text_surface = SVG_ICONS["chart_surface"]

        view_mode_options = [
            ("line", svg_text_line),
            ("surface", svg_text_surface)
        ]

        self.view_mode_selector = SegmentControl(items=view_mode_options, default_value=self.plot_state.view_mode)
        self.view_mode_selector.selectionChanged.connect(self.handle_view_mode_change)

        cards_layout.addWidget(self.view_mode_selector, alignment=Qt.AlignBottom)

        layout.addLayout(title_layout)
        layout.addWidget(desc_lbl)
        layout.addLayout(cards_layout)
        
        return header_widget
        

    def _create_info_card(self, title, value):
        card = QFrame()
        card.setFixedSize(160, 70)
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setProperty("class", UI_TAG.BG_CARD_SECONDARY)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(0)
        
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", UI_TAG.TEXT_ACCENT)
        
        lbl_value = QLabel(value)
        lbl_value.setProperty("class", UI_TAG.TEXT_PRIMARY)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        return card
    

    def showEvent(self, event):
        super().showEvent(event)
        
        if self._is_theme_dirty:
            self.apply_theme()
            self._is_theme_dirty = False
        




        
