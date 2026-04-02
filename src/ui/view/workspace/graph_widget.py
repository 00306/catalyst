import os
import tempfile
from PyQt5.QtWidgets import QWidget, QStackedLayout, QSizePolicy, QApplication
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, Qt, QEvent, QCoreApplication
from src.ui.builder.multi_detector_plot_builder import MultiDetectorPlotBuilder
from src.ui.builder import MainPlotBuilder
import traceback
from src.ui.state.plot_state import PlotState
from src.bridge.plot_interaction_bridge import PlotInteractionBridge
import json
import numpy as np
from src.ui.view.dialog.file_dialog import FileDialog
from src.core.theme.tokens import UI_TAG
from src.core.theme.theme_manager import ThemeManager
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

class GraphWidget(QWidget):
    sig_render_finish = pyqtSignal()
    sig_clicked_sample = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._is_html_ready = False 
        self._pending_pkg = None


        self.init_ui()
        self.setup_bridge()

    def init_ui(self):
        self.setProperty("class", UI_TAG.BG_GRAPH_AREA)
        self.theme_manager = ThemeManager()
        self.builder = MainPlotBuilder(self.theme_manager.get_resolved_theme(), self.theme_manager.get_graph_theme())

        self.z_stack = QStackedLayout(self) 
        self.z_stack.setStackingMode(QStackedLayout.StackAll)
        self.z_stack.setContentsMargins(0, 0, 0, 0)
        self.z_stack.setSpacing(0)
        


        self.browser = QWebEngineView()
        self.browser.page().setBackgroundColor(Qt.transparent)
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)
        if self.browser.focusProxy():
            self.browser.focusProxy().installEventFilter(self)
        self.browser.installEventFilter(self)

        self.browser.loadFinished.connect(self._on_load_finished)
        
        self._init_html()

        self.z_stack.addWidget(self.browser)

        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        profile = self.browser.page().profile()
        try:
            profile.downloadRequested.disconnect()
        except TypeError:
            pass
        
        profile.downloadRequested.connect(self.handle_download)


    def _init_html(self):
        html = self.builder._init_html()

        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"init_graph_{id(self)}.html")
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath(temp_file_path)))
        
    def apply_theme(self, current_theme, current_graph_theme):
        self.set_loading(True, current_theme)
        self._rebuild_graph(current_theme, current_graph_theme)

    def _rebuild_graph(self, current_theme, current_graph_theme):
        self.load_plot_data(
            self._last_plot_state, 
            self._last_metadata, 
            self._last_color_map,
            current_theme,
            current_graph_theme
        )

    def handle_download(self, download_item):
        default_filename = download_item.suggestedFileName()

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", default_filename)

        icon_color = self.theme_manager.get_resolved_theme()["text_primary"]

        dialog = FileDialog(
            parent=self, 
            icon_color=icon_color,
            title="Save Capture", 
            default_dir=desktop_path,
            filter_str="PNG (*.png);;JPEG (*.jpg *.jpeg);;All Files (*.*)", 
            mode="save"
        )

        if dialog.exec_():
            paths = dialog.selectedFiles()
            if paths:
                save_path = paths[0]
                download_item.setPath(save_path)
                download_item.accept()         

    def showEvent(self, event):
        super().showEvent(event)
        if self.browser.focusProxy():
            self.browser.focusProxy().installEventFilter(self)

    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'viewport'):
                    QCoreApplication.sendEvent(parent.viewport(), event)
                    return True
                parent = parent.parent()

        if event.type() == QEvent.NativeGesture:
            event.accept()
            return True

        if event.type() == QEvent.Gesture:
            event.accept()
            return True
                
                
        return super().eventFilter(obj, event)

    def setup_bridge(self):
        self.bridge = PlotInteractionBridge()
        self.bridge.clicked_signal.connect(self.handle_sample_click)
        self.bridge.render_finished_signal.connect(self._on_render_finished)

        self.channel = QWebChannel()
        self.channel.registerObject("pyBridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

    def handle_sample_click(self, name):
        self.sig_clicked_sample.emit(name)

    def _on_render_finished(self):
        self.z_stack.setCurrentIndex(0)
        self.sig_render_finish.emit()

    def _on_load_finished(self, ok):
        if ok: 
            css_reset_script = """
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `
                html, body { overflow: hidden !important; background-color: transparent !important; }
                .plot-area { width: 100% !important; height: 100% !important; }
            `;

            document.head.appendChild(style);
            """
            self.browser.page().runJavaScript(css_reset_script)

            self._is_html_ready = True
            if self._pending_pkg:
                self._execute_render(self._pending_pkg)
                self._pending_pkg = None

    def load_plot_data(self, plot_state: PlotState, metadata, color_map, current_theme, current_graph_theme):
        self._last_plot_state = plot_state
        self._last_metadata = metadata
        self._last_color_map = color_map

        try:
            current_det = metadata.default_detector
            current_unit = metadata.z_unit_dict.get(current_det, "Unknown")

            self.builder = MainPlotBuilder(theme=current_theme, graph_theme=current_graph_theme)

            self.builder.with_data(plot_state.curr_X, plot_state.curr_Y, plot_state.curr_Z, color_map) \
                .with_sample_names(metadata.sample_names) \
                .with_cos_data(plot_state.cos_time_axis, plot_state.avg_Z, plot_state.cos_sync_Z, plot_state.cos_async_Z) \
                .with_view_mode(plot_state.view_mode) \
                .with_detector_info(current_det, current_unit) \
            

            self.render_all_plot()

        except Exception as e:

            print(f"❌ [GraphWidget] 렌더링 중 오류 발생: {e}")
            traceback.print_exc()

    def render_all_plot(self):
        pkg = self.builder.get_full_render_package()

        if not self._is_html_ready:
            self._pending_pkg = pkg
            return

        self._execute_render(pkg)


    def _execute_render(self, pkg):
        try:
            data_to_save = {
                "hm": pkg['hm'],
                "d3": pkg['d3'],
                "sync": pkg['sync'],
                "async": pkg['async']
            }
            json_string = json.dumps(data_to_save)

            js_content = f"window.__TEMP_PLOT_DATA__ = {json_string};"

            temp_file_path = os.path.join(tempfile.gettempdir(), f"plot_data_{id(self)}.js")
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(js_content)

            file_url = QUrl.fromLocalFile(os.path.abspath(temp_file_path)).toString()

            theme_json = json.dumps(pkg['theme'])
            script = f"window.loadDataScript({theme_json}, '{file_url}');"

            self.browser.page().runJavaScript(script)

        except Exception as e:
            print(f"❌ 데이터 파일 생성 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()



    def update_cos_data_only(self, time_axis, sync_z, async_z, avg_z):
        limit_sync = float(np.nanpercentile(np.abs(sync_z), 99.9)) or 1e-5
        limit_async = float(np.nanpercentile(np.abs(async_z), 99.9)) or 1e-5

        if len(avg_z) > 0:
            max_1d_height = float(np.max(avg_z)) * 1.1
        else:
            max_1d_height = 1.0

        time_json = json.dumps(time_axis.tolist())
        sync_json = json.dumps(sync_z.tolist())
        async_json = json.dumps(async_z.tolist())
        avg_json = json.dumps(avg_z.tolist())
        
        script = f"if(window.updateCosData) {{ window.updateCosData({time_json}, {sync_json}, {async_json}, {limit_sync}, {limit_async}, {max_1d_height}, {avg_json}); }}"
        self.browser.page().runJavaScript(script)

    def update_range_only(self, start_t, end_t):
        script = f"if(window.updateIntegrationRange) window.updateIntegrationRange({start_t}, {end_t});"
        self.browser.page().runJavaScript(script)

    def update_multi_graph(self, times, intensity_A, intensity_B, metadata, current_view_mode):
        try:
            temp_file = os.path.join(
                tempfile.gettempdir(), 
                f"render_multi_{metadata.project_name}_{id(self)}.html"
            )

            extra = getattr(metadata, 'extra', {})
            det_A = extra.get("detector_A", "Detector A")
            det_B = extra.get("detector_B", "Detector B")
            sample_name = metadata.sample_names[0] if metadata.sample_names else "Unknown"

            builder = MultiDetectorPlotBuilder(times, intensity_A, intensity_B)
            builder.with_metadata(det_A, det_B, sample_name) \
                   .render(save_path=temp_file)

            self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath(temp_file)))

        except Exception as e:
            print(f"❌ [GraphWidget] Multi 렌더링 오류: {e}")


    def set_x_range(self, start_t: float, end_t: float):
        js_code = f"""
        (function() {{
            var graphDiv = document.getElementById('plot_3d');
            if (graphDiv && typeof Plotly !== 'undefined') {{
                var update = {{ 'scene.xaxis.range': [{start_t}, {end_t}] }};
                Plotly.relayout(graphDiv, update);
            }}
        }})();
        """
        
        self.browser.page().runJavaScript(js_code, lambda result: self.sig_render_finish.emit())

    def set_loading(self, is_loading, current_theme):
        if is_loading:
            theme_json_str = json.dumps(current_theme)
            self.browser.page().runJavaScript(f"WebLoading.init({theme_json_str});")
            QApplication.processEvents()            
        else:
            self.browser.page().runJavaScript("WebLoading.hide();")

        