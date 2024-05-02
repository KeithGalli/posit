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

ui.input_select(  
    "select",  
    "Select an option below:",  
    ['Dallas (TX)', 'Boston (MA)', 'Los Angeles (CA)', 'San Francisco (CA)', 'Seattle (WA)', 'Atlanta (GA)',
    'New York City (NY)', 'Portland (OR)', 'Austin (TX)','Portland (ME)'],  
)

@render_altair
def sales_over_time():
    df = dat()
    df['date'] = pd.to_datetime(df['order_date'])
    df['month'] = df['date'].dt.month_name()
    # Define the order of the months to ensure they appear chronologically
    month_order = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
    
    # Creating a month order for sorting in Altair
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
    counts = df.groupby(["month", "city"])['quantity_ordered'].sum().reset_index()
    city_counts = counts[counts['city']==input.select()]
    # Create the Altair chart
    chart = alt.Chart(city_counts).mark_bar().encode(
        x='month',
        y='quantity_ordered',
        tooltip=['city', 'month', 'quantity_ordered']
    ).properties(
        title=f'Sales Over Time in {input.select()}'
    ).configure_axis(
        labelAngle=0  # Adjust label angle if needed
    )
    return chart

ui.input_numeric("item_count", "Number of items to show", 1, min=1, max=20)  

@render_plotly
def top_sellers():
    df = dat()
    top_5_products = df.groupby("product")["quantity_ordered"].sum().nlargest(input.item_count()).reset_index()
    fig = px.bar(top_5_products, x="product", y="quantity_ordered")

    return fig

@render.plot
def time_heatmap():
    # Step 1: Extract the hour from the order_date
    df = dat()
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['hour'] = df['order_date'].dt.hour

    # Step 2: Aggregate data by hour
    hourly_counts = df['hour'].value_counts().sort_index()

    # Step 3: Prepare data for heatmap (optional: create a dummy dimension if needed)
    # For simplicity, let's assume you want to view by hours (24 hrs) and just map counts directly.
    heatmap_data = np.zeros((24, 1))  # 24 hours, 1 dummy column
    for hour in hourly_counts.index:
        heatmap_data[hour, 0] = hourly_counts[hour]

    # Convert heatmap data to integer if needed
    heatmap_data = heatmap_data.astype(int)

    # Step 4: Plot with Seaborn
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="coolwarm", cbar=False, xticklabels=[], yticklabels=[f"{i}:00" for i in range(24)])
    plt.title("Number of Orders by Hour of Day")
    plt.ylabel("Hour of Day")
    plt.xlabel("Order Count")

@render.ui
def heatmap():
    # Create a map centered roughly in the middle of the US
    df = dat()
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    # Prepare the data for the HeatMap; each entry in heatmap_data is (lat, lon, weight)
    heatmap_data = [(lat, long, qty) for lat, long, qty in zip(df['lat'],df['long'], df['quantity_ordered'])]
    # Add HeatMap to the map
    HeatMap(heatmap_data).add_to(map)

    return map
        

@render.data_frame
def frame():
    return dat().head(1000)