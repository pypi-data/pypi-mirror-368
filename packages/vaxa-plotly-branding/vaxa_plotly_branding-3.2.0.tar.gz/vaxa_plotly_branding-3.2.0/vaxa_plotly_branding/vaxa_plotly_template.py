import pathlib

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image

_colorway = px.colors.qualitative.G10
_colorway[2] = px.colors.qualitative.G10[0]
_colorway[0] = "#FBAA36"
_colorway[5] = "#00A7B5"

vaxa_colorway = _colorway

logo_path = pathlib.Path(__file__).parent / "vaxa_analytics_plot_logo.png"

# Try to load logo image safely
logo_image = None
if logo_path.exists():
    try:
        logo_image = Image.open(logo_path)
    except Exception:
        logo_image = None

# noinspection PyTypeChecker
VaxaBrandingTemplate = go.layout.Template(
    layout=go.Layout(
        title_font=dict(family="Darker Grotesque", size=36),
        width=1200,
        height=800,
        font=dict(family="Plus Jakarta Sans", size=14),
        colorway=_colorway,
        yaxis_automargin="left+top",
        xaxis_automargin="left+right",
        margin=dict(b=100, pad=10),
        images=(
            [
                dict(
                    name="logo",
                    source=logo_image,
                    xref="paper",
                    yref="paper",
                    x=-0.05,
                    y=-0.1,
                    sizex=0.4,
                    sizey=0.4,
                    xanchor="left",
                    yanchor="top",
                )
            ]
            if logo_image
            else []
        ),
        # legend settings
        showlegend=True,
        legend_title="Legend",
        legend_bgcolor="rgba(230,231,232,0.5)",
    ),
)

VaxaBrandingTemplateNoLogo = go.layout.Template(
    layout=go.Layout(
        title_font=dict(family="Darker Grotesque", size=36),
        width=1200,
        height=800,
        font=dict(family="Plus Jakarta Sans", size=14),
        colorway=_colorway,
        yaxis_automargin="left+top",
        xaxis_automargin="left+right",
        margin=dict(b=100, pad=10),
        # legend settings
        showlegend=True,
        legend_title="Legend",
        legend_bgcolor="rgba(230,231,232,0.5)",
    ),
)

pio.templates["vaxa_analytics"] = VaxaBrandingTemplate
pio.templates["vaxa_analytics_no_logo"] = VaxaBrandingTemplateNoLogo
