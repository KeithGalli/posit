from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from shiny import reactive
from shiny.express import render, ui, input
from shinywidgets import render_plotly, render_altair
import plotly.express as px
import folium
from folium.plugins import HeatMap
import seaborn as sns

# Header Section with Logo and Title
with ui.div(class_="header-container"):
    with ui.div(class_="logo-container"):
        @render.image
        def image():
            dir = Path(__file__).resolve().parent
            img = {"src": str(dir / "assets/shiny.png")}
            return img

    with ui.div(class_="title-container"):
        ui.h2("Sales Dashboard - Part 5 of 5")

ui.tags.style("""
    h2 {
        background-color: #5DADE2;
        color: white;
        padding: 10px;
        text-align: center;
        margin: 0;
        display: inline-block;
    }

    .header-container {
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        background-color: #5DADE2;
        margin: 10px;
    }

    .logo-container {
        height: 100%;
    }

    .logo-container img {
        height: 40px;
        margin-right: 5px;
    }

    body {
        background-color: #5DADE2;
    }
""")

def apply_common_styles(fig):
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": "Arial, sans-serif", "size": 12, "color": "darkblue"},
            "colorway": px.colors.sequential.Blues,
            "xaxis_title": None
        }
    )
    return fig

@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales.csv"
    return pd.read_csv(infile)

# Set common font and color palette for Altair
_ = alt.themes.register(
    "custom_theme",
    lambda: {
        "config": {
            "axis": {
                "labelFontSize": 12,
                "titleFontSize": 14,
                "labelFont": "Arial",
                "titleFont": "Arial",
                "labelColor": "darkblue",
                "titleColor": "darkblue",
                "grid": False,
                "tickSize": 0,
                "titleFontWeight": "normal",
            },
            "view": {"strokeWidth": 0},
            "background": "#FFFFFF",
            "font": "Arial",
        }
    }
)
_ = alt.themes.enable("custom_theme")

with ui.card(full_screen=True):
    ui.card_header("Sales by City in 2023")
    with ui.layout_sidebar():
        with ui.sidebar(open="open", bg="#f8f8f8"):
            ui.input_select(
                "select",
                "Select an option below:",
                [
                    "Dallas (TX)",
                    "Boston (MA)",
                    "Los Angeles (CA)",
                    "San Francisco (CA)",
                    "Seattle (WA)",
                    "Atlanta (GA)",
                    "New York City (NY)",
                    "Portland (OR)",
                    "Austin (TX)",
                    "Portland (ME)",
                ],
            )

        @render_altair
        def sales_over_time():
            df = dat()
            df["date"] = pd.to_datetime(df["order_date"])
            df["month"] = df["date"].dt.month_name()
            month_order = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)
            counts = df.groupby(["month", "city"], observed=True)["quantity_ordered"].sum().reset_index()
            city_counts = counts[counts["city"] == input.select()]

            chart = (
                alt.Chart(city_counts)
                .mark_bar(color="#3585BF")
                .encode(
                    x=alt.X("month", title="Month"),
                    y=alt.Y("quantity_ordered", title="Quantity Ordered"),
                    tooltip=["city", "month", "quantity_ordered"],
                )
                .configure_axis(labelAngle=0)
            )
            return chart

with ui.layout_columns(widths=1 / 2):
    with ui.navset_card_underline(
        footer=ui.input_numeric("items", "Number of Items", 5, min=1, max=10, step=None, width=0.5)
    ):
        with ui.nav_panel("Top Sellers"):
            @render_plotly
            def top_sellers():
                df = dat()
                top_5_products = df.groupby("product")["quantity_ordered"].sum().nlargest(input.items()).reset_index()
                fig = px.bar(top_5_products, x="product", y="quantity_ordered")
                fig.update_traces(marker_color=top_5_products["quantity_ordered"], marker_colorscale="Blues")
                fig.update_layout(yaxis_title="Quantity Ordered")
                apply_common_styles(fig)
                return fig

        with ui.nav_panel("Top Sellers Value ($)"):
            @render_plotly
            def top_sellers_value():
                df = dat()
                df["value"] = df["quantity_ordered"] * df["price_each"]
                top_5_products = df.groupby("product")["value"].sum().nlargest(input.items()).reset_index()
                fig = px.bar(top_5_products, x="product", y="value")
                fig.update_traces(marker_color=top_5_products["value"], marker_colorscale="Blues")
                fig.update_layout(yaxis_title="Value ($)")
                apply_common_styles(fig)
                return fig

        with ui.nav_panel("Lowest Sellers"):
            @render_plotly
            def lowest_sellers():
                df = dat()
                top_5_products = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nsmallest(input.items())
                    .reset_index()
                    .sort_values("quantity_ordered", ascending=False)
                )
                fig = px.bar(top_5_products, x="product", y="quantity_ordered")
                fig.update_traces(marker_color=top_5_products["quantity_ordered"], marker_colorscale="Reds")
                fig.update_layout(yaxis_title="Quantity Ordered")
                apply_common_styles(fig)
                return fig

        with ui.nav_panel("Lowest Sellers Value ($)"):
            @render_plotly
            def lowest_sellers_value():
                df = dat()
                df["value"] = df["quantity_ordered"] * df["price_each"]
                top_5_products = (
                    df.groupby("product")["value"]
                    .sum()
                    .nsmallest(input.items())
                    .reset_index()
                    .sort_values("value", ascending=False)
                )
                fig = px.bar(top_5_products, x="product", y="value")
                fig.update_traces(marker_color=top_5_products["value"], marker_colorscale="Reds")
                fig.update_layout(yaxis_title="Value ($)")
                apply_common_styles(fig)
                return fig

    with ui.navset_card_underline():
        with ui.nav_panel("Number of Orders by Hour of Day"):
            @render.plot
            def time_heatmap():
                df = dat()
                df["order_date"] = pd.to_datetime(df["order_date"])
                df["hour"] = df["order_date"].dt.hour
                hourly_counts = df["hour"].value_counts().sort_index()
                heatmap_data = np.zeros((24, 1))
                for hour in hourly_counts.index:
                    heatmap_data[hour, 0] = hourly_counts[hour]
                heatmap_data = heatmap_data.astype(int)

                plt.figure(figsize=(10, 8))
                sns.heatmap(
                    heatmap_data,
                    annot=True,
                    fmt="d",
                    cmap="Blues",
                    cbar=False,
                    xticklabels=[],
                    yticklabels=[f"{i}:00" for i in range(24)],
                )
                plt.yticks(color="darkblue")
                plt.ylabel("Hour of Day", fontname="Arial", color="darkblue", fontsize=12)
                plt.xlabel("Order Count", fontname="Arial", color="darkblue", fontsize=12)

with ui.navset_card_underline():
    with ui.nav_panel("Sales Locations"):
        @render.ui
        def heatmap():
            df = dat()
            map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
            heatmap_data = [(lat, long, qty) for lat, long, qty in zip(df["lat"], df["long"], df["quantity_ordered"])]
            custom_gradient = {
                0.0: "#E3F2FD",
                0.2: "#BBDEFB",
                0.4: "#64B5F6",
                0.6: "#42A5F5",
                0.8: "#2196F3",
                1.0: "#1976D2",
            }
            HeatMap(heatmap_data, gradient=custom_gradient).add_to(map)
            return map

with ui.navset_card_underline():
    with ui.nav_panel("Dataframe Sample"):
        @render.data_frame
        def frame():
            return dat().head(1000)