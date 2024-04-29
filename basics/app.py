from pathlib import Path

import pandas
import matplotlib.pyplot as plt

from shiny import reactive
from shiny.express import render, ui


@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales_new.csv"
    return pandas.read_csv(infile)

@render.plot
def total_orders():
    df = dat()
    top_5_products = df.groupby("Product")["Quantity Ordered"].sum().nlargest(5)
    top_5_products.plot(kind="bar")

@render.plot
def total_orders2():
    # Assuming top_5_products contains the sum of 'Quantity Ordered' for the top 5 products
    df = dat()
    top_5_products = df.groupby("Product")["Quantity Ordered"].sum().nlargest(5)

    # Create the bar plot
    ax = top_5_products.plot(kind="bar", color='skyblue', figsize=(10, 6))

    # Set x-tick labels with rotation
    plt.xticks(rotation=45, ha='right')  # Rotates the x-axis labels to 45 degrees and aligns them to the right

    plt.xlabel('Product')  # Label for the x-axis
    plt.ylabel('Quantity Ordered')  # Label for the y-axis
    plt.title('Top 5 Products by Quantity Ordered')  # Title of the plot
    # plt.tight_layout()  # Adjusts subplot params so that the subplot(s) fits in to the figure area.
    return ax

with ui.navset_card_underline():
    with ui.nav_panel("Data frame"):
        @render.data_frame
        def frame():
            # Give dat() to render.DataGrid to customize the grid
            return dat()


