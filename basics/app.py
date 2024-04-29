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

@render.plot
def total_orders():
    df = dat()
    top_5_products = df.groupby("Product")["Quantity Ordered"].sum().nlargest(5)
    top_5_products.plot(kind="bar")

@render_plotly
def total_orders2():
    df = dat()
    top_5_products = df.groupby("Product")["Quantity Ordered"].sum().largest(5)

    fig = px.bar(top_5_products, x=top_5_products.index, y="Quantity Ordered")
    return fig

with ui.navset_card_underline():
    with ui.nav_panel("Data frame"):
        @render.data_frame
        def frame():
            # Give dat() to render.DataGrid to customize the grid
            return dat()


