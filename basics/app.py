from pathlib import Path

import pandas
import matplotlib.pyplot as plt

from shiny import reactive
from shiny.express import render, ui

from shinywidgets import render_plotly, render_widget
import plotly.express as px

import folium
from folium.plugins import HeatMap

@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales_with_coords.csv"
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

            fig.update_traces(marker_color=top_5_products["Quantity Ordered"], marker_colorscale='Reds')
            apply_common_styles(fig)
            return fig
        
with ui.navset_card_underline():
    with ui.nav_panel("Sales Locations"):
        @render.ui
        def heatmap():
            # Create a map centered roughly in the middle of the US
            df = dat()
            map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

            # Prepare the data for the HeatMap; each entry in heatmap_data is (lat, lon, weight)
            heatmap_data = [(lat, long, qty) for lat, long, qty in zip(df['lat'],df['long'], df['Quantity Ordered'])]
            # Add HeatMap to the map
            HeatMap(heatmap_data).add_to(map)

            return map

with ui.navset_card_underline():
    with ui.nav_panel("Data frame"):
        @render.data_frame
        def frame():
            # Give dat() to render.DataGrid to customize the grid
            return dat()


