import numpy as np
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

class ChromatogramPlotBuilder:
    def __init__(self, signals, color_map, selected_index=None):
        self.signals = signals
        self.selected_index = selected_index
        self.color_map = color_map
        self.normalize = False

        self.theme = {
            "bg_base": "#323232",
            "bg_card": "#2B2B2B",
            "border": "#404040",
            "title_text": "#64D2FF",
            "text": "#A0A0A0",
            "bg_paper": "#2B2B2B",
            "grid_line": "#454545",
            "axis_line": "#404040",
            "axis_title": "#A0A0A0",
            "guide_line": "rgba(255, 255, 255, 0.4)",
            "slice_line": "#E0E0E0"
        }


    def with_theme(self, theme_dict):
        if theme_dict:
            self.theme.update(theme_dict)
        return self

    def with_color(self, hex_color):
        self.color = hex_color
        return self
    
    def with_normalization(self):
        self.normalize = True
        return self

    def build(self):
        fig = go.Figure()
        step = 1

        current_unit = ""
        if self.signals:
            current_unit = self.signals[0].unit

        if self.selected_index is not None and 0 <= self.selected_index < len(self.signals):
            sig = self.signals[self.selected_index]
            y_data = sig.intensity
            unit = sig.unit
            method_val = sig.method
            
            if self.normalize:
                max_val = np.max(y_data)
                y_data = y_data / max_val if max_val != 0 else y_data

            x_data_plot = sig.time[::step].tolist()
            y_data_plot = y_data[::step].tolist()

            highlight_color = self.color_map.get(sig.sample_name, "#00beff")

            fig.add_trace(go.Scattergl(
                x=x_data_plot,
                y=y_data_plot,
                mode="lines",
                line=dict(color=highlight_color, width=3), 
                name=sig.sample_name,
                showlegend=False,
                hovertemplate=(
                    f"<b>%{{fullData.name}}</b><br>"
                    f"🧪 Method: {method_val}</span><br>"
                    f"RT: %{{x:.2f}} min<br>"
                    f"Signal: %{{y:,.1f}} {unit}<br>"
                    "<extra></extra>"
                )
            ))

        for i, sig in enumerate(self.signals):
            if i == self.selected_index: continue
            
            y_data = sig.intensity

            if self.normalize:
                max_val = np.max(y_data)
                y_data = y_data / max_val if max_val != 0 else y_data

            x_data_plot = sig.time[::step].tolist()
            y_data_plot = y_data[::step].tolist()

            base_hex = self.color_map.get(sig.sample_name, "#787878")

            try:
                r, g, b = hex_to_rgb(base_hex)
                ghost_color = f'rgba({r}, {g}, {b}, 0.15)'
            except ValueError:
                ghost_color = 'rgba(120, 120, 120, 0.15)'

            fig.add_trace(go.Scattergl(
                x=x_data_plot,
                y=y_data_plot,
                mode='lines',
                line=dict(color=ghost_color, width=2),
                name=sig.sample_name,
                hoverinfo='skip',
                showlegend=False,
            ))


        bg_paper = self.theme["bg_paper"]
        text_color = self.theme["text"]
        grid_color = self.theme["grid_line"]
        axis_color = self.theme["axis_line"]
        axis_title = self.theme["axis_title"]
        crosshair_theme = {
            "sliceLineColor": self.theme["slice_line"]
        }

        y_axis_label = f"Intensity ({current_unit})"

        fig.update_layout(
            hovermode='closest',
            paper_bgcolor=bg_paper,
            plot_bgcolor=bg_paper,
            margin=dict(l=80, r=20, t=20, b=50),
            autosize=True,
            showlegend=False,
            font=dict(color=text_color),
            xaxis=dict(
                title=dict(
                    text="Retention Time (min)",
                    font=dict(color=axis_title, size=12)
                ),
                gridcolor=grid_color,
                linecolor=axis_color,
                showgrid=True,
                zeroline=False,
                tickfont=dict(color=axis_title),
                automargin=True
            ),
            yaxis=dict(
                title=dict(
                    text=y_axis_label,
                    font=dict(color=axis_title, size=12)
                ),
                autorange=True, 
                gridcolor=grid_color,
                linecolor=axis_color,
                showgrid=True, 
                zeroline=False,
                tickfont=dict(color=axis_title),
                automargin=True
            ),

            meta=crosshair_theme
        )

        return fig
