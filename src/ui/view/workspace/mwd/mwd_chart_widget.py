import plotly.graph_objects as go
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtCore import QEvent, QTimer, Qt, QCoreApplication, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import numpy as np
import os
import tempfile
from src.core.theme.theme_manager import ThemeManager
from plotly.offline import get_plotlyjs

class DebugWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"🌐 [JS 로그] {message}")


class MWDChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

        self._is_js_ready = False
        self._pending_data = None

        self.selected_idx = None
        self.mwd_data_list = []

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.browser = QWebEngineView()
        self.browser.setPage(DebugWebPage(self.browser))
        self.browser.page().setBackgroundColor(Qt.transparent)
        self.main_layout.addWidget(self.browser)

        self.theme_manager = ThemeManager()
        self.current_theme = self.theme_manager.get_resolved_theme()
        self.current_graph_theme = self.theme_manager.get_graph_theme()

        self._init_html()
        self.browser.loadFinished.connect(self._on_load_finished)

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

    def on_theme_changed(self, current_theme, current_graph_theme):
        self.current_theme = current_theme
        self.current_graph_theme = current_graph_theme

        self._init_html() 
        self._render_plot()

    def _init_html(self):
        bg_base = self.current_graph_theme["bg_base"]
        border = self.current_graph_theme["border"]
        title_text = self.current_graph_theme["text_accent"]

        plotly_js = get_plotlyjs()

        base_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <script type="text/javascript">
            (function() {{
                var origInsertRule = CSSStyleSheet.prototype.insertRule;
                CSSStyleSheet.prototype.insertRule = function(rule, index) {{
                    try {{
                        return origInsertRule.call(this, rule, index);
                    }} catch(e) {{
                        console.warn("CSS rule skipped: " + rule.substring(0, 50));
                        return -1;
                    }}
                }};
            }})();
            </script>
            <script type="text/javascript">
            __PLOTLY_JS__;
            </script>
            <style>
                body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background-color: {bg_base}; }}
                #plot {{ 
                    position: absolute; 
                    top: 0; 
                    left: 0; 
                    right: 0; 
                    bottom: 0; 
                    border-radius: 16px;
                    background-color: {bg_base};
                    overflow: hidden;
                    border: 1px solid {border};
                }}

                #title {{
                    position: absolute;
                    top: 15px;
                    left: 20px;
                    color: {title_text};
                    font-family: sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    z-index: 10;
                    pointer-events: none;
                }}
            </style>
        </head>
        <body>
            <div id="plot"></div>
            <div id="title">MWD</div> 
            <script>
                window.updateChart = function(jsonStr) {{
                    try {{
                        const figure = JSON.parse(jsonStr);
                        console.log("JSON 파싱 성공", figure.data.length);
                        if(figure.data.length > 0) {{
                            const sampleY = figure.data[0].y;
                            console.log("📊 [데이터 체크] 첫 번째 트레이스 Y값 샘플:", sampleY.slice(0, 5));
                            console.log("📊 [데이터 체크] Y값 최대치:", Math.max(...sampleY.filter(v => !isNaN(v))));
                        }}

                        const plotEl = document.getElementById('plot');

                        Plotly.react(plotEl, figure.data, figure.layout, {{
                            displayModeBar: false,
                            scrollZoom: false,
                            staticPlot: false,
                            doubleClick: false,
                        }});

                        setTimeout(() => {{
                            Plotly.Plots.resize(plotEl);
                        }}, 10);


                    }} catch (e) {{
                        console.error("[JS Error]" + e.message);
                    }}
                }};
            
            </script>
        </body>
        </html>
        """

        base_html = base_html.replace("__PLOTLY_JS__", plotly_js)

        tmp_path = os.path.join(tempfile.gettempdir(), f"mwd_plot_{id(self)}.html")
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(base_html)
        self.browser.setUrl(QUrl.fromLocalFile(tmp_path))

    def _on_load_finished(self, ok):
            if ok:

                self._is_js_ready = True
                if self._pending_data:
                    
                    data_to_send = self._pending_data 
                    self._pending_data = None 
                    
                    QTimer.singleShot(200, lambda d=data_to_send: self.browser.page().runJavaScript(d))
                else:
                    self._render_plot()

    def update_mwd_chart(self, mwd_data_list, selected_idx, color_map):
        
        self.mwd_data_list = mwd_data_list
        self.selected_idx = selected_idx
        self.color_map = color_map
        
        self._render_plot()

    def clear_all(self):
        self.mwd_data_list.clear()
        self._render_plot()

    def _render_plot(self):
        fig = go.Figure()

        if not hasattr(self, 'mwd_data_list') or not self.mwd_data_list:
            pass

        else:
            for i, data in enumerate(self.mwd_data_list):
                if data is None or i == self.selected_idx: 
                    continue

                s_name = data.get('name', 'Unknown')
                base_hex = self.color_map.get(s_name, "#787878")
                
                r, g, b = int(base_hex[1:3], 16), int(base_hex[3:5], 16), int(base_hex[5:7], 16)
                ghost_color = f'rgba({r}, {g}, {b}, 0.2)'



                x_arr = np.array(data['x'])
                y_arr = np.array(data['y'])
                sorted_indices = np.argsort(x_arr)

                is_selected = (i == self.selected_idx)

                fig.add_trace(go.Scatter(
                    x=x_arr[sorted_indices].tolist(),
                    y=y_arr[sorted_indices].tolist(),
                    mode='lines',
                    line=dict(color=ghost_color, width=2, shape='spline'), 
                    name=f"{s_name} (bg)",
                    hoverinfo='skip',
                    showlegend=False
                ))

            if self.selected_idx is not None and 0 <= self.selected_idx < len(self.mwd_data_list):
                data = self.mwd_data_list[self.selected_idx]
                if data is not None:
                    s_name = data.get('name', 'Selected')
                    
                    highlight_color = self.color_map.get(s_name, "#00beff")

                    x_arr = np.array(data["x"])
                    y_arr = np.array(data["y"])
                    indices = np.argsort(x_arr)

                    x_sorted = x_arr[indices]
                    y_sorted = y_arr[indices]
                    
                    real_mw = 10 ** x_sorted



                    fig.add_trace(go.Scatter(
                        x=x_arr[indices].tolist(),
                        y=y_arr[indices].tolist(),
                        customdata=real_mw.tolist(),
                        mode='lines',
                        name=s_name,
                        line=dict(color=highlight_color, width=3, shape='spline'), 
                        hovertemplate=(
                            f"<b>{s_name}</b><br>"
                            "MW: %{customdata:,.0f} Da<br>"
                            "Log MW: %{x:.2f}<br>"
                            "dW/dLogM: %{y:.3f}"
                            "<extra></extra>"
                        ),
                        showlegend=False
                    ))
        
        # 여기 graph theme인거 구분해줘야함
        bg_paper = self.current_graph_theme["bg_paper"]
        text_color = self.current_graph_theme["text"]
        grid_color = self.current_graph_theme["grid_line"]
        axis_title = self.current_graph_theme["axis_title"]

        fig.update_layout(
            paper_bgcolor=bg_paper,
            plot_bgcolor=bg_paper,
            margin=dict(l=80, r=20, t=40, b=40),
            autosize=True,
            dragmode=False,
            hovermode='closest',
            showlegend=False,
            font=dict(color=text_color),
            xaxis=dict(
                title="Log MW",
                range=[9, 0],
                gridcolor=grid_color,
                linecolor=grid_color,
                showgrid=True,
                zeroline=False,
                autorange=True,
                tickfont=dict(color=axis_title)
            ),
            yaxis=dict(
                title="dW / dLogM",
                autorange=True, 
                gridcolor=grid_color,
                linecolor=grid_color,
                showgrid=True, 
                zeroline=False,
                tickfont=dict(color=axis_title)
            ),
        )

        json_data = fig.to_json()
        js_code = "window.updateChart(`%s`);" % json_data
        
        if not self._is_js_ready:
            self._pending_data = js_code
            return
        
        self.browser.page().runJavaScript(js_code)