from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import altair as alt

from shiny import reactive
from shiny.express import render, ui, input

from shinywidgets import render_plotly, render_widget, render_altair
import plotly.express as px

import folium
from folium.plugins import HeatMap

import seaborn as sns


@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales_with_coords.csv"
    return pd.read_csv(infile)

with ui.card(full_screen=True):  
    ui.card_header("Sales by City in 2023")
    with ui.layout_sidebar():  
        with ui.sidebar(open="open", bg="#f8f8f8"):
            ui.input_select(  
                "select",  
                "Select an option below:",  
               ['Dallas (TX)', 'Boston (MA)', 'Los Angeles (CA)', 'San Francisco (CA)', 'Seattle (WA)', 'Atlanta (GA)',
                'New York City (NY)', 'Portland (OR)', 'Austin (TX)','Portland (ME)'],  
            )

        @render_plotly
        def sales_over_time():
            df = dat()
            df['date'] = pd.to_datetime(df['order_date'])
            df['month'] = df['date'].dt.month_name()
            # Define the order of the months to ensure they appear chronologically
            month_order = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"]
            counts = df.groupby(["month", "city"])['quantity_ordered'].sum().reset_index()
            city_counts = counts[counts['city']==input.select()]
            fig = px.bar(city_counts, x='month', y='quantity_ordered', title=f'Sales Over Time {input.select()}',
                            category_orders={"month": month_order})
            fig.update_layout(showlegend=False)
            return fig

with ui.layout_columns(widths=1/2):

    with ui.navset_card_underline():
        with ui.nav_panel("Top Sellers"):
            ui.input_numeric("items", "Number of Items", 5, min=1, max=20, step=None, width=.5)
            @render_plotly
            def top_sellers():
                df = dat()
                top_5_products = df.groupby("product")["quantity_ordered"].sum().nlargest(input.items()).reset_index()
                fig = px.bar(top_5_products, x="product", y="quantity_ordered")
                fig.update_layout(xaxis_title="Product", yaxis_title="Quantity Ordered")
                return fig
            
        with ui.nav_panel("Top Sellers Value ($)"):
            "Bar Chart Top Sellers Value"
        with ui.nav_panel("Lowest Sellers"):
            "Bar Chart Lowest Sellers"
        with ui.nav_panel("Lowest Sellers Value ($)"):
            "Bar Chart Lowest Sellers Value"
        
    with ui.card():
        "Heatmap here"
            
with ui.navset_card_underline():
    with ui.nav_panel("Sales Locations"):
        "US Map of sales"
        
with ui.navset_card_underline():
    with ui.nav_panel("Dataframe Sample"):
        @render.data_frame
        def frame():
            return dat().head(1000)