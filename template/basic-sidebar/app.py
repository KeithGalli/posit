import seaborn as sns

# Import data from shared.py
from shared import df
from shiny.express import input, render, ui

ui.page_opts(title="POSITive Electronics Sales")

with ui.sidebar():
    choices = ["Boston", "New York City", "Atlanta", "Portland", "Seattle", "Los Angeles", "Austin", "San Francisco"]
    ui.input_selectize("var", "Select variable", choices=choices, multiple=True, selected=["Boston", "New York City"])
    # ui.input_switch("species", "Group by species", value=True)
    # ui.input_switch("show_rug", "Show Rug", value=True)


@render.plot
def hist():
    sales_by_city = df.groupby(["city"])["Quantity Ordered"].sum().reset_index()
    city = sales_by_city[sales_by_city["city"].isin(input.var())]
    if len(city) != 0:
        city.plot(x="city", y="Quantity Ordered", kind="bar")

@render.data_frame
def show_df():
    if len(input.var()) > 0:
        return df[df['city'].isin(input.var())]