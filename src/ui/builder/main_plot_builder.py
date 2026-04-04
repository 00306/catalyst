import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.core.preprocessor import apply_gaussian_smoothing, normalize_min_max
from src.util.resource_path import resource_path
from plotly.offline import get_plotlyjs

class MainPlotBuilder:
    def __init__(self, theme, graph_theme):
        self.X = None
        self.Y = None
        self.Z = None
        self.color_map = None
        
        self.cos_time_axis = None
        self.avg_Z = None
        self.cos_sync_Z = None
        self.cos_async_Z = None

        self.cut_percentage = 0.0
        self.box_size = (10.0, 10.0, 5.0)
        self.cmap_name = 'Turbo'
        self.labels = {"x": "Retention Time (min)", "y": "Samples", "z": "Normalized Intensity"}
        self.use_smooth_surf = False

        self.view_mode = "line"
        self.line_width = 3
        self.theme = theme
        self.graph_theme = graph_theme

    def with_data(self, X, Y, Z, color_map=None):
        self.X = np.copy(X)
        self.Y = np.copy(Y)
        self.Z = np.copy(Z)
        if color_map is not None:
            self.color_map = color_map
        return self

    def with_cos_data(self, time_axis, avg_Z, sync_Z, async_Z):
        self.cos_time_axis = time_axis
        self.avg_Z = avg_Z
        self.cos_sync_Z = sync_Z
        self.cos_async_Z = async_Z
        
        return self


    def with_view_mode(self, mode):
        self.view_mode = mode
        return self

    def with_smooth_surf(self, sigma=1.0):
        self.use_smooth_surf = True
        self.smooth_sigma = sigma
        return self

    def with_sample_names(self, names):
        self.sample_names = names
        return self

    def with_truncation(self, percentage=0.35):
        self.cut_percentage = percentage
        return self

    def with_box_size(self, x=10.0, y=10.0, z=5.0):
        self.box_size = (x, y, z)
        return self

    def with_labels(self, xlabel="Retention Time", ylabel="Sample", zlabel="Intensity"):
        self.labels = {"x": xlabel, "y": ylabel, "z": zlabel}
        return self

    def with_detector_info(self, name, unit):
        self.detector_name = name
        self.z_unit = unit
        return self
    
    def _init_html(self):
        plotly_js = get_plotlyjs()
        
        with open(resource_path("asset/js/loading.js"), 'r', encoding='utf-8') as f:
            web_loading_js = f.read()

        with open(resource_path("asset/html/main_plot_template.html"), 'r', encoding='utf-8') as f:
            template = f.read()

        theme_json = json.dumps(self.theme)

        html = template.replace("__PLOTLY_JS__", plotly_js)
        html = html.replace("__WEB_LOADING_JS__", web_loading_js)
        html = html.replace("__THEME_JSON__", theme_json)

        return html
    
    def get_full_render_package(self):
        ctx = self._prepare_render_context()
        
        fig_hm = self._build_heatmap_figure(ctx)
        fig_3d = self._build_3d_figure(ctx)
        fig_sync = self._build_cos_figure(ctx, is_sync=True)
        fig_async = self._build_cos_figure(ctx, is_sync=False)

        package = {
            "theme": self.graph_theme,
            "hm": json.loads(fig_hm.to_json()),
            "d3": json.loads(fig_3d.to_json()),
            "sync": json.loads(fig_sync.to_json()),
            "async": json.loads(fig_async.to_json())
        }

        return package
    

    def _prepare_render_context(self):
        cur_X, cur_Y, cur_Z, cur_Z_raw = self._process_data()
        y_pos, original_y_labels, hover = self._prepare_hover_data(cur_Y, cur_Z_raw)
        
        y_min, y_max = np.min(self.Y) - 5, np.max(self.Y) + 5
        hm_ratio = (y_max - y_min) / (np.max(self.X) - np.min(self.X))
        y_labels = [f"Sample {i+1}" for i in range(len(original_y_labels))]
        
        return {
            "X": cur_X, "Y": cur_Y, "Z": cur_Z, "hover": hover,
            "y_pos": y_pos, "y_labels": y_labels,
            "y_range": (y_min, y_max), "hm_ratio": hm_ratio,
            "t_range": (np.min(self.cos_time_axis), np.max(self.cos_time_axis))
        }
    
    def _build_3d_figure(self, ctx):
        fig = go.Figure()
        if self.view_mode == "surface":
            fig.add_trace(self._create_surface_trace(ctx["X"], ctx["Y"], ctx["Z"], ctx["hover"]))
        else:
            for t in self._create_line_traces(ctx["X"], ctx["Y"], ctx["Z"], ctx["hover"]):
                fig.add_trace(t)
        self._apply_layout_3d(fig, ctx["y_pos"], ctx["y_labels"])
        return fig
    

    def _build_heatmap_figure(self, ctx):
        fig = go.Figure(data=[self._create_heatmap_trace(ctx["X"], ctx["Y"], ctx["Z"])])
        self._apply_layout_hm(fig, ctx["hm_ratio"], *ctx["y_range"], ctx["y_pos"], ctx["y_labels"])
        return fig

    def _build_cos_figure(self, ctx, is_sync=True):
        cos_traces = self._create_contour_traces()
        trace = cos_traces[0] if is_sync else (cos_traces[1] if len(cos_traces) > 1 else None)
        fig = self.create_cos_subplot_grid(trace)
        self._apply_layout_cos_grid(fig, *ctx["t_range"], is_sync=is_sync)
        return fig
    
    def _process_data(self):
        cur_X = np.copy(self.X)
        cur_Y = np.copy(self.Y)
        cur_Z_raw = np.copy(self.Z)
        cur_Z = normalize_min_max(cur_Z_raw)

        if self.use_smooth_surf:
            cur_Z = apply_gaussian_smoothing(cur_Z, sigma=self.smooth_sigma)

        return cur_X, cur_Y, cur_Z, cur_Z_raw
    
    def _prepare_hover_data(self, cur_Y, cur_Z_raw):
        y_positions = np.unique(cur_Y)
        y_labels = []
        
        for y_val in y_positions:
            idx = int(round(y_val / 10.0))
            if hasattr(self, 'sample_names') and 0 <= idx < len(self.sample_names):
                name = self.sample_names[idx]
            else:
                name = f"Sample {idx}"
            y_labels.append(name)

        hover_text = np.empty_like(cur_Z_raw, dtype=object)
        for i in range(cur_Y.shape[0]):
            y_val = cur_Y[i, 0]
            sample_idx = int(round(y_val / 10.0))
            s_name = self.sample_names[sample_idx] if hasattr(self, 'sample_names') and 0 <= sample_idx < len(self.sample_names) else f"Sample {sample_idx}"
            hover_text[i, :] = s_name
        
        hover_bundle = np.stack((hover_text, cur_Z_raw), axis=-1)
        hover_bundle_swapped = np.transpose(hover_bundle, (1, 0, 2))
        
        return y_positions, y_labels, hover_bundle_swapped
    
    def _create_marginal_line(self, position = "top"):
        line_color = self.graph_theme["plot_line"]

        if position == "top":
            return go.Scatter(
                x=self.cos_time_axis, 
                y=self.avg_Z,
                mode='lines',
                line=dict(color=line_color, 
                          width=1,
                          shape='spline',
                          smoothing=1.0
                          ),
                showlegend=False,
                hoverinfo='x+y'
            )
        
        elif position == "right":
            return go.Scatter(
                x=self.avg_Z,
                y=self.cos_time_axis,
                mode='lines',
                line=dict(color=line_color, 
                          width=1,
                          shape='spline',
                          smoothing=1.0
                          ),
                showlegend=False,
                hoverinfo='x+y'
            )


    def _create_line_traces(self, cur_X, cur_Y, cur_Z, hover_bundle):
        traces = []

        for i in range(cur_Z.shape[0]):
            x_val = cur_X[i, :]
            y_val = cur_Y[i, :]
            z_val = cur_Z[i, :]


            s_name = self.sample_names[i] if hasattr(self, 'sample_names') and i < len(self.sample_names) else f"Sample {i}"
            line_color = self.color_map.get(s_name, "#0A84FF")

            traces.append(go.Scatter3d(
                x=x_val, y=y_val, z=z_val,
                mode='lines',
                name=s_name,
                surfaceaxis=2,
                surfacecolor=line_color,
                opacity=0.9,
                line=dict(
                    color=line_color,
                    width=4
                ),
                hovertemplate=(
                    f"<b>Sample:</b> {s_name}<br>" +
                    "RT: %{x:.3f} min<br>" +
                    "Intensity: %{z:.4f}<extra></extra>"
                )
            ))
        return traces

    def _create_surface_trace(self, cur_X, cur_Y, cur_Z, hover_bundle):
        colorscale = [
            [0, 'rgba(0, 0, 131, 0.98)'], [0.125, 'rgba(0, 0, 255, 0.98)'],
            [0.375, 'rgba(0, 255, 255, 0.98)'], [0.625, 'rgba(255, 255, 0, 0.98)'],
            [0.875, 'rgba(255, 0, 0, 0.98)'], [1, 'rgba(128, 0, 0, 0.98)']
        ]
        return go.Surface(
            x=cur_X, y=cur_Y, z=cur_Z,
            colorscale=colorscale,
            customdata=hover_bundle,
            hovertemplate=(
                "<b>Sample: %{customdata[0]}</b><br>" +
                f"Raw Intensity: %{{customdata[1]:.4f}} {self.z_unit}<br>" +
                "<b>Retention Time:</b> %{x:.3f} min<br>" +
                "Normalized: %{z:.4f}<extra></extra>"
            ),
            lighting=dict(ambient=0.6, diffuse=1.0, fresnel=2.0, roughness=0.5, specular=0),
            colorbar=dict(thickness=15, len=0.55, x=1.0, tickfont=dict(size=10))
        )
    
    def _create_heatmap_trace(self, cur_X, cur_Y, cur_Z):
        hm_x = cur_X[0, :] if cur_X.ndim == 2 else cur_X
        hm_y = cur_Y[:, 0] if cur_Y.ndim == 2 else cur_Y
        colorscale = [
            [0, 'rgba(0, 0, 131, 0.98)'], [0.125, 'rgba(0, 0, 255, 0.98)'],
            [0.375, 'rgba(0, 255, 255, 0.98)'], [0.625, 'rgba(255, 255, 0, 0.98)'],
            [0.875, 'rgba(255, 0, 0, 0.98)'], [1, 'rgba(128, 0, 0, 0.98)']
        ]
        return go.Heatmap(
            x=hm_x, y=hm_y, z=cur_Z,
            colorscale=colorscale,
            showscale=False, hoverinfo='skip'
        )
    
    def _create_contour_traces(self):
        traces = []
        transparent_colorscale = [
            [0.0, 'rgba(44, 123, 182, 1.0)'],
            [0.5, 'rgba(0, 0, 0, 0.0)'],
            [1.0, 'rgba(215, 25, 28, 1.0)']
        ]

        if len(self.cos_time_axis) > 1:
            dt = self.cos_time_axis[1] - self.cos_time_axis[0]
            shifted_axis = self.cos_time_axis - (dt / 2.0)
        else:
            shifted_axis = self.cos_time_axis

        min_t = self.cos_time_axis[0]
        max_t = self.cos_time_axis[-1]
        line_color = self.graph_theme["plot_line"]

        if self.cos_sync_Z is not None:
            z_data_sync = self.cos_sync_Z
            limit_sync = np.nanpercentile(np.abs(z_data_sync), 99.9)
            limit_sync = limit_sync if limit_sync > 0 else 1e-5

            traces.append(go.Contour(
                x=shifted_axis, y=shifted_axis, z=z_data_sync,
                name="CosSyncLayer",
                colorscale=transparent_colorscale,
                zmid=0, zmax=limit_sync, zmin=-limit_sync,
                ncontours=15,
                showscale=False,
                contours=dict(showlines=True, coloring='heatmap', labelfont=dict(size=8, color='white')),
                line=dict(color=line_color, width=0.6),
                colorbar=dict(title=dict(text="Sync Corr", font=dict(size=10)), thickness=10, len=0.3, x=1.05, y=0.525),
                hovertemplate="RT 1: %{x:.3f} min<br>RT 2: %{y:.3f} min<br>Sync: %{z:.4f}<extra></extra>"
            ))

        if self.cos_async_Z is not None:
            z_data_async = self.cos_async_Z
            limit_async = np.nanpercentile(np.abs(z_data_async), 99.9)
            limit_async = limit_async if limit_async > 0 else 1e-5

            traces.append(go.Contour(
                x=self.cos_time_axis, y=self.cos_time_axis, z=z_data_async,
                name="CosAsyncLayer",
                colorscale=transparent_colorscale,
                zmid=0, zmax=limit_async, zmin=-limit_async,
                ncontours=15,
                showscale=False,
                contours=dict(showlines=True, coloring='heatmap', labelfont=dict(size=8, color='white')),
                line=dict(color=line_color, width=0.6),
                colorbar=dict(title=dict(text="Async Corr", font=dict(size=10)), thickness=10, len=0.3, x=1.05, y=0.145),
                hovertemplate="RT 1: %{x:.3f} min<br>RT 2: %{y:.3f} min<br>Async: %{z:.4f}<extra></extra>"
            ))

        return traces
    
    def create_cos_subplot_grid(self, contour_trace):
        fig = make_subplots(
            rows = 2, cols = 2,
            column_widths=[0.95, 0.05],
            row_heights=[0.05, 0.95],
            vertical_spacing=0.02,
            horizontal_spacing=0.02,
            specs=[
            [{"type": "xy"},           None],         
            [{"type": "contour"},      {"type": "xy"}]
            ],
            shared_xaxes=True,
            shared_yaxes=True
            )
        
        fig.add_trace(contour_trace, row=2, col=1)
        fig.add_trace(self._create_marginal_line(position="top"), row=1, col=1)
        fig.add_trace(self._create_marginal_line(position="right"), row=2, col=2)


        return fig
    
    def _apply_common_style(self, fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial, Helvetica, sans-serif", size=10, color=self.graph_theme["text"]),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40, pad=4),
            modebar=dict(
                bgcolor='rgba(0,0,0,0)',
                color=self.theme["text_primary"],
                activecolor=self.theme["text_accent"],
            )

        )
    
    def _apply_layout_3d(self, fig, y_positions, y_labels):
        self._apply_common_style(fig)

        grid_color = self.graph_theme["grid_line"]
        axis_color = self.graph_theme["axis_line"]

        fig.update_layout(
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title=dict(text="Retention Time (min)", font=dict(size=12)), gridcolor=grid_color, tickfont=dict(size=12, color=self.graph_theme["text"]), showline=True, mirror=True, linecolor=axis_color, linewidth=2, showbackground=False, zeroline=False),
                yaxis=dict(title="", 
                           tickmode='array', 
                           tickvals=y_positions, 
                           ticktext=y_labels, 
                           tickfont=dict(size=12, color=self.graph_theme["text"]), 
                           gridcolor=grid_color, 
                           showline=True, 
                           mirror=True, 
                           linecolor=axis_color, 
                           linewidth=2, 
                           showbackground=False, 
                           zeroline=False),

                zaxis=dict(title=dict(text="Intensity (a.u.)", font=dict(size=12)), gridcolor=grid_color, showline=True, tickfont=dict(size=12, color=self.graph_theme["text"]), linecolor=axis_color, showbackground=False, linewidth=2, zeroline=False, mirror=True),
                camera=dict(projection=dict(type="perspective"), eye=dict(x=1.6, y=-1.6, z=1.2)),
                aspectmode='manual', 
                aspectratio=dict(x=self.box_size[0]/10.0, y=self.box_size[1]/10.0, z=self.box_size[2]/10.0),
                
            )
        )

    def _apply_layout_hm(self, fig, heatmap_ratio, y_plot_min, y_plot_max, y_positions, y_labels):
        self._apply_common_style(fig)

        axis_color = self.graph_theme["axis_line"]

        fig.update_layout(
            xaxis=dict(title=dict(text="Retention Time (min)", font=dict(size=10, color=self.graph_theme["text"])), 
                       showgrid=False, 
                       automargin=False, 
                       showline=False, 
                       linecolor=axis_color, 
                       mirror=True, 
                       range=[np.min(self.X), np.max(self.X)], 
                       zeroline=False, 
                       constrain="domain"),
            yaxis=dict(showline=False, showticklabels=True, showgrid=False, linecolor=axis_color, mirror=True, 
                    scaleanchor="x", scaleratio=1/heatmap_ratio, range=[y_plot_min, y_plot_max], zeroline=False,
                    tickmode='array',
                    tickvals=y_positions,
                    ticktext=y_labels),
            dragmode=False,
        )
    def _apply_layout_cos_grid(self, fig, min_t, max_t, is_sync=True):
        self._apply_common_style(fig)
        grid_color = self.graph_theme["grid_line"]
        axis_color = self.graph_theme["axis_line"]

        main_axis_config = dict(
            showgrid=True, 
            range=[min_t, max_t],
            gridcolor=grid_color,
            autorange=False,
            dtick=10,
            nticks=15,
            ticks="inside",
            showline=True,
            tickmode="auto",
            linewidth=1,
            tickwidth=1,
            tickfont=dict(size=12, color=self.graph_theme["text"]),
            linecolor=axis_color,
            mirror="ticks",
            zeroline=False,
            constrain="domain",
        )

        fig.update_xaxes(
            **main_axis_config,
            title=dict(text="Retention Time (min)", font=dict(size=10, color=self.graph_theme["text"])),
            
            row=2, col=1
        )

        fig.update_yaxes(
            **main_axis_config,
            title=dict(text="Retention Time (min)", font=dict(size=10, color=self.graph_theme["text"])),
            scaleanchor="x2",
            scaleratio=1,
            
            row=2, col=1
        )

        fig.update_xaxes(
            range=[min_t, max_t],
            visible=False,
            showgrid=False, showticklabels=False, 
            linecolor=axis_color, linewidth=1, mirror=False,
            row=1, col=1
        )
        fig.update_yaxes(
            showgrid=False, showticklabels=False,
            visible=False,
            linecolor=axis_color,
            range=[0, np.max(self.avg_Z) * 1.1],
            row=1, col=1,
            automargin=False
        )

        fig.update_xaxes(
            showgrid=False, showticklabels=False,
            linecolor=axis_color,
            visible=False,
            automargin=False,
            range=[0, np.max(self.avg_Z) * 1.1],
            row=2, col=2
        )
        fig.update_yaxes(
            range=[min_t, max_t],
            showgrid=False, showticklabels=False, 
            visible=False,
            automargin=False,
            linecolor=axis_color, linewidth=1, mirror=False,
            row=2, col=2
        )

        fig.update_layout(
            dragmode=False,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0, pad=0),
            hoverdistance=100,
            
            shapes=[
                dict(
                    type="line",
                    xref="x2", yref="y2",
                    x0=min_t, y0=min_t,
                    x1=max_t, y1=max_t,
                    line=dict(color=self.graph_theme["text"], width=0.5, dash="2px 2px"),
                    layer="above"
                ),
            ]
        )
        
        return fig