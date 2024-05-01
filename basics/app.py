from pathlib import Path

import pandas
import matplotlib.pyplot as plt

from shiny import reactive
from shiny.express import render, ui, input

from shinywidgets import render_plotly, render_widget
import plotly.express as px

import folium
from folium.plugins import HeatMap

@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales_with_coords.csv"
    return pandas.read_csv(infile)

with ui.card(full_screen=True):  
    ui.card_header("Sales by City in 2023")

    with ui.layout_sidebar():  
        with ui.sidebar(open="desktop", bg="#f8f8f8"):
            ui.input_select(  
                "select",  
                "Select an option below:",  
                ["Atlanta", "Boston", "New York City", "San Francisco", "Dallas"],  
            )  

            
        @render_plotly
        def sales_over_time():
            df = dat()
            df['date'] = pandas.to_datetime(df['order_date'])
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
        
