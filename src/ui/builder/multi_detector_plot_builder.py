import plotly.graph_objects as go

class MultiDetectorPlotBuilder:
    def __init__(self, times, intensity_A, intensity_B):
        self.times = times
        self.intensity_A = intensity_A
        self.intensity_B = intensity_B
        
        # 기본 메타데이터 설정
        self.det_A = "Detector A"
        self.det_B = "Detector B"
        self.sample_name = "Unknown Sample"

    def with_metadata(self, det_A, det_B, sample_name):
        self.det_A = det_A
        self.det_B = det_B
        self.sample_name = sample_name
        return self
    
    def render(self, save_path):
        fig = go.Figure()

        fig.add_trace(go.Scatter3d(
            x=self.times,
            y=self.intensity_A,
            z=self.intensity_B,
            mode='lines',
            line=dict(
                color=self.times,
                colorscale='Plasma',
                width=8
            ),
            hovertemplate=(
                f"<b>Time:</b> %{{x:.2f}} min<br>" +
                f"<b>{self.det_A}:</b> %{{y:.4f}}<br>" +
                f"<b>{self.det_B}:</b> %{{z:.4f}}<extra></extra>"
            )
        ))

        off_white = "#F8F9FA"  
        off_black = "#1A1A1A"

        fig.update_layout(
            paper_bgcolor=off_white,
            plot_bgcolor=off_white,
            font=dict(family="Pretendard, sans-serif", size=12, color=off_black),
            margin=dict(l=0, r=0, b=0, t=40),
            scene=dict(
                xaxis_title="Retention Time (min)",
                yaxis_title=f"{self.det_A} Intensity",
                zaxis_title=f"{self.det_B} Intensity",
                aspectmode='cube', 
                camera=dict(
                    projection=dict(type="perspective"),
                    eye=dict(x=-1.5, y=-1.5, z=1.2)
                )
            )
        )

        fig.write_html(save_path, include_plotlyjs=True)