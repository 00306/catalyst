from PyQt5.QtWidgets import QFrame, QScrollArea, QWidget, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QEvent, QTimer, pyqtSignal, QCoreApplication, QUrl
from src.ui.builder.chromatogram_plot_builder import ChromatogramPlotBuilder
from src.bridge.plot_interaction_bridge import PlotInteractionBridge
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from src.core.theme.tokens import UI_TAG
import tempfile, os
from src.util.resource_path import resource_path
from plotly.offline import get_plotlyjs

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        print(f"JS Console: {msg} (line {line})")

class ChromatogramWidget(QWidget):
    slice_changed_signal = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self._is_js_ready = False
        self._init_ui()
        self._setup_style()
        self._load_base_html()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.card_frame = QFrame(self)
        self.card_frame.setProperty("class", UI_TAG.BG_GRAPH_AREA)
        self.card_frame.setStyleSheet("""
            #QFrame {
                border-radius: 20px;      
            }
        """)

        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setSpacing(0)
        self.card_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("Chromatogram")
        self.title_label.setProperty("class", UI_TAG.TEXT_ACCENT)
        self.title_label.setStyleSheet("""
        QLabel {
            padding-left: 12px;
            padding-top: 12px;
        }
        """)
        self.title_label.setFixedHeight(40)
        self.card_layout.addWidget(self.title_label, 0)

        self.browser = QWebEngineView()
        self.custom_page = CustomWebPage(self.browser)
        self.browser.setPage(self.custom_page)

        self.bridge = PlotInteractionBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("plotBridge", self.bridge)

        self.browser.page().setWebChannel(self.channel)
        
        self.card_layout.addWidget(self.browser)
        
        self.bridge.slice_changed_signal.connect(self.handle_slice_changed_signal)
        self.browser.loadFinished.connect(self._on_load_finished)

        self.layout.addWidget(self.card_frame)


    def handle_slice_changed_signal(self, start_time, end_time):
        self.slice_changed_signal.emit(start_time, end_time)


    def on_theme_changed(self, current_graph_theme):
        self.card_frame.style().unpolish(self.card_frame)
        self.card_frame.style().polish(self.card_frame)

        self._rebuild_graph(current_graph_theme)


    def _on_load_finished(self, ok):
        if ok:
            self._is_js_ready = True
            if hasattr(self, '_pending_data') and self._pending_data:
                self.browser.page().runJavaScript(self._pending_data)
                self._pending_data = None

    def _on_js_ready(self):
        self._is_js_ready = True

        if self._pending_data:

            QTimer.singleShot(50, lambda: self.browser.page().runJavaScript(self._pending_data))
            self._pending_data = None


    def set_bar_lock(self, should_lock):
        lock_val = "true" if should_lock else "false"
        script = f"if(window.setBarLockState) {{ window.setBarLockState({lock_val}); }}"
        
        if not self._is_js_ready:
            self._pending_lock = script
            return

        self.browser.page().runJavaScript(script)

    def _load_base_html(self):

        plotly_js = get_plotlyjs()

        with open(resource_path("asset/html/chromatogram_plot_template.html"), 'r', encoding='utf-8') as f:
            html_content = f.read()


        with open(resource_path("asset/js/crosshair.js"), 'r', encoding='utf-8') as f:
            js_content = f.read()

        html = html_content.replace("__PLOTLY_JS__", plotly_js)
        final_html = html.replace("/* CROSSHAIR_JS_PLACEHOLDER */", js_content)
        
        tmp_path = os.path.join(tempfile.gettempdir(), "chromatogram_plot.html")
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

        self.browser.setUrl(QUrl.fromLocalFile(tmp_path))

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

    def _setup_style(self):
        self.browser.page().setBackgroundColor(Qt.transparent)
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)
        self.browser.settings().setAttribute(self.browser.settings().ShowScrollBars, False)

    def wheelEvent(self, event):
        event.ignore()

        parent = self.parent()
        while parent:
            if isinstance(parent, QScrollArea):
                parent.wheelEvent(event)
                break
            parent = parent.parent()

    def _rebuild_graph(self, current_graph_theme):
        self.update_plot(self._last_signals, self._last_color_map, current_graph_theme, self._last_selected_index)


    def update_plot(self, signals: list, color_map, current_graph_theme, selected_index: int = None):
        self._last_signals = signals
        self._last_color_map = color_map
        self._last_selected_index = selected_index

        self.builder = ChromatogramPlotBuilder(signals, color_map, selected_index)

        self.builder.with_theme(current_graph_theme)
        
        fig = self.builder.build()
        json_data = fig.to_json()

        script = f"window.updateChart(`{json_data}`);"
        
        if not self._is_js_ready:
            self._pending_data = script
            return

        self.browser.page().runJavaScript(script)

    def showEvent(self, event):
        super().showEvent(event)
        if self.browser.focusProxy():
            self.browser.focusProxy().installEventFilter(self)
