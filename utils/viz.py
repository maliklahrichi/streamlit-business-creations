"""Chart functions (consistent style, labelled axes and units).

Colour rule: a colour always means a legal form (amber = micro-entrepreneurs,
blue = companies, brick = sole proprietors excl. micro, ink = total). Direction of
change is shown by position (left/right of zero), never by a second colour code.
The three hues were checked with the palette validator (all pairs, colour-blind
simulation, contrast >= 3:1 on white).
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import constants as C

INK, MUTED, GRID = "#14213D", "#52607A", "#E3E7ED"
FORM_COLORS = {
    "Total": INK,
    "Micro-entrepreneurs": "#C77F00",
    "Companies": "#0072B2",
    "Sole proprietors (excl. micro)": "#8E2C1F",
}
FONT = dict(family="Atkinson, sans-serif", size=14, color=INK)
HOVER = dict(bgcolor="white", bordercolor=INK, font=dict(family="Atkinson, sans-serif", size=14, color=INK))


def _layout(fig, height=420):
    fig.update_layout(
        title=None, height=height, font=FONT, margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", y=1.04, x=0, yanchor="bottom", title_text="",
                    font=dict(size=14)),
        hovermode="x unified", hoverlabel=HOVER,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    tick = dict(size=13, color=MUTED)
    fig.update_xaxes(showgrid=False, linecolor=MUTED, tickcolor=MUTED, tickfont=tick,
                     title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=tick, title_font=dict(color=MUTED))
    return fig


def _dash_total(fig):
    """The total is a reference, not a legal form: dashed ink line."""
    fig.for_each_trace(lambda t: t.update(line=dict(dash="dash", color=INK)) if t.name == "Total" else None)


def index_lines(df, base_year):
    """Base-100 lines by legal form + marker for the 2023 series break."""
    fig = px.line(
        df, x="annee", y="indice", color="forme_legale", markers=True,
        color_discrete_map=FORM_COLORS,
        labels={"annee": "Year", "indice": f"Index (base 100 = {base_year})"},
    )
    fig.update_traces(line_width=2.8, marker_size=8)
    _dash_total(fig)
    fig.add_hline(y=100, line_dash="dot", line_color=MUTED, line_width=1)
    fig.add_vline(x=C.BREAK_YEAR, line_dash="dash", line_color=MUTED, line_width=1)
    fig.add_annotation(
        x=C.BREAK_YEAR, y=0, yref="paper", showarrow=False, xanchor="right", yanchor="bottom",
        text="2023: counting method changed ", font=dict(size=12, color=MUTED),
    )
    # Fixed range: the annotation text must not stretch the axis (no empty future years)
    x0, x1 = int(df["annee"].min()), int(df["annee"].max())
    fig.update_xaxes(range=[x0 - 0.25, x1 + 0.25], dtick=1 if x1 - x0 <= 10 else None)
    return _layout(fig)


def trend_lines(df):
    """Seasonally adjusted monthly creations, by legal form (axis starts at zero)."""
    fig = px.line(
        df, x="date", y="creations", color="forme_legale",
        color_discrete_map=FORM_COLORS,
        labels={"date": "Month", "creations": "Creations per month (seasonally adjusted)"},
    )
    fig.update_traces(line_width=2.4, hovertemplate="%{y:,.0f}")
    _dash_total(fig)
    break_date = f"{C.BREAK_YEAR}-01-01"
    fig.add_shape(type="line", x0=break_date, x1=break_date, y0=0, y1=1, yref="paper",
                  line=dict(dash="dash", color=MUTED, width=1))
    fig.add_annotation(
        x=break_date, y=1, yref="paper", showarrow=False, xanchor="left",
        text=" 2023: counting method changed", font=dict(size=12, color=MUTED),
    )
    if df["date"].min() <= pd.Timestamp("2020-03-01"):
        # Spring 2020 lockdown: a visible dip that would otherwise puzzle the reader
        fig.add_shape(type="rect", x0="2020-03-01", x1="2020-05-31", y0=0, y1=1,
                      yref="paper", fillcolor=MUTED, opacity=0.14, line_width=0, layer="below")
        fig.add_annotation(
            x="2020-03-01", y=1, yref="paper", showarrow=False, xanchor="right",
            text="COVID-19 lockdown ", font=dict(size=12, color=MUTED),
        )
    fig.update_yaxes(rangemode="tozero", tickformat=",")
    return _layout(fig)


def sector_bars(df, form_label):
    """Horizontal bars: change in the number of creations by sector (colour = legal form)."""
    df = df.sort_values("variation")
    fig = go.Figure(go.Bar(
        x=df["variation"], y=df["secteur_court"], orientation="h",
        marker_color=FORM_COLORS[form_label],
        customdata=df[["debut", "fin", "variation_pct"]],
        hovertemplate="<b>%{y}</b><br>Start: %{customdata[0]:,.0f}"
                      "<br>End: %{customdata[1]:,.0f}"
                      "<br>Change: %{x:+,.0f} (%{customdata[2]:+.0f}%)<extra></extra>",
    ))
    fig.update_xaxes(title=f"Change in number of creations ({form_label})", tickformat=",")
    fig.update_yaxes(title="", automargin=True)
    fig.update_layout(hovermode="closest")
    return _layout(fig, height=440)


def _ramp(color, signed):
    """Sequential ramp towards the legal-form colour; diverging only if both signs occur."""
    neutral = "#EEF1F5"
    return ([[0, "#7A5195"], [0.5, neutral], [1, color]] if signed else [[0, neutral], [1, color]])


def dept_map(df, geojson, value_col, label, color=INK):
    """Choropleth map of the mainland départements (with a clear hover box)."""
    is_var = value_col == "variation_pct"
    signed = bool(is_var and df[value_col].min() < 0 < df[value_col].max())
    fig = px.choropleth(
        df, geojson=geojson, locations="code_geo", featureidkey="properties.code",
        color=value_col, hover_name="lieu",
        custom_data=["creations_debut", "creations_fin", "variation_pct"],
        color_continuous_scale=_ramp(color, signed),
        color_continuous_midpoint=0 if signed else None,
        labels={value_col: label},
    )
    fig.update_traces(
        marker_line_width=0.6, marker_line_color="white",
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Change: %{customdata[2]:+.1f}%<br>"
            "Creations: %{customdata[0]:,.0f} → %{customdata[1]:,.0f}"
            "<extra></extra>"
        ),
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        height=560, margin=dict(l=0, r=0, t=10, b=0), font=FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title=label, thickness=12, len=0.6, outlinewidth=0),
        hoverlabel=HOVER,
    )
    return fig


def rank_bars(df, value_col, label, pct=True, color=INK):
    """Horizontal ranking (top or bottom N), by % change or by number of creations."""
    df = df.sort_values(value_col)
    change = "%{x:+.1f}%" if pct else "%{x:+,.0f} creations (%{customdata[2]:+.1f}%)"
    fig = go.Figure(go.Bar(
        x=df[value_col], y=df["lieu"], orientation="h",
        marker_color=color,
        customdata=df[["creations_debut", "creations_fin", "variation_pct"]],
        hovertemplate=("<b>%{y}</b><br>Change: " + change +
                       "<br>Creations: %{customdata[0]:,.0f} → %{customdata[1]:,.0f}"
                       "<extra></extra>"),
    ))
    fig.update_xaxes(title=label, tickformat="," if not pct else None)
    fig.update_yaxes(title="", automargin=True)
    fig.update_layout(hovermode="closest")
    return _layout(fig, height=360)
