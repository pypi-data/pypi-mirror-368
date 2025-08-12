import plotly.graph_objects as go 
import polars as pl

def polars_to_html(df: pl.DataFrame) -> str:
    return df._repr_html_()

def fig_to_html(fig: go.Figure) -> str:
    return fig.to_html(full_html = False)

def collapsable(html: str, title: str) -> str:
    return f'<details><summary>{title}</summary>' + html + '</details>'