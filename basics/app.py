from pathlib import Path

import pandas
import matplotlib.pyplot as plt

from shiny import reactive
from shiny.express import render, ui

from shinywidgets import render_plotly
import plotly.express as px


@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales_new.csv"
    return pandas.read_csv(infile)

def apply_common_styles(fig):
    # Set the background to transparent
    fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',  # Transparent plot background
        'paper_bgcolor': 'rgba(0,0,0,0)',  # Transparent figure background
        'font': {'family': "Arial, sans-serif", 'size': 12, 'color': "darkblue"}
    })
    return fig

with ui.navset_card_underline():
    with ui.nav_panel("Sales over time"):
        "ehlllo"

with ui.navset_card_underline():
    with ui.nav_panel("Top Sellers"):
        @render_plotly
        def top_sellers():
            df = dat()
            top_5_products = df.groupby("Product")["Quantity Ordered"].sum().nlargest(5).reset_index()

            print(top_5_products.head())

            fig = px.bar(top_5_products, x="Product", y="Quantity Ordered")

            fig.update_traces(marker_color=top_5_products["Quantity Ordered"], marker_colorscale='Blues')
            apply_common_styles(fig)
            return fig
        
    with ui.nav_panel("Lowest Sellers"):
        @render_plotly
        def lowest_sellers():
            df = dat()
            top_5_products = df.groupby("Product")["Quantity Ordered"].sum().nsmallest(5).reset_index()

            fig = px.bar(top_5_products, x="Product", y="Quantity Ordered")

            fig.update_traces(marker_color=top_5_products["Quantity Ordered"], marker_colorscale='Blues')
            apply_common_styles(fig)
            return fig

with ui.navset_card_underline():
    with ui.nav_panel("Data frame"):
        @render.data_frame
        def frame():
            # Give dat() to render.DataGrid to customize the grid
            return dat()


