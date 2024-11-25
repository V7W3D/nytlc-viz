import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
from datetime import date

taxi_zones = gpd.read_file('../Data/taxi_zones_final/taxi_zones_final.shp')
yellow_pickup_counts = pd.read_parquet('../Data/yellow_pickup_counts.parquet')
yellow_dropoff_counts = pd.read_parquet('../Data/yellow_dropoff_counts.parquet')
green_pickup_counts = pd.read_parquet('../Data/green_pickup_counts.parquet')
green_dropoff_counts = pd.read_parquet('../Data/green_dropoff_counts.parquet')

yellow_pickup_counts['date'] = pd.to_datetime(yellow_pickup_counts['date'])
yellow_dropoff_counts['date'] = pd.to_datetime(yellow_dropoff_counts['date'])
green_pickup_counts['date'] = pd.to_datetime(green_pickup_counts['date'])
green_dropoff_counts['date'] = pd.to_datetime(green_dropoff_counts['date'])

taxi_type = st.selectbox("Choisissez le type de taxi :", ["Jaune", "Vert"])
view_type = st.radio("Choisissez la vue :", ["Pickup", "Dropoff"])

selected_date = st.date_input(
    "Choisissez une date :",
    min_value=min(yellow_pickup_counts['date'].min(), green_pickup_counts['date'].min()),
    max_value=max(yellow_pickup_counts['date'].max(), green_pickup_counts['date'].max())
)

if taxi_type == "Jaune":
    data_source = yellow_pickup_counts if view_type == "Pickup" else yellow_dropoff_counts
elif taxi_type == "Vert":
    data_source = green_pickup_counts if view_type == "Pickup" else green_dropoff_counts

filtered_data = data_source[data_source['date'] == pd.Timestamp(selected_date)]

m = folium.Map([40.7, -74], zoom_start=10, tiles="cartodbpositron")

folium.Choropleth(
    geo_data=taxi_zones,
    name="choropleth",
    data=filtered_data,
    columns=["LocationID", "count"],
    key_on="feature.properties.OBJECTID",
    nan_fill_color="yellow",
    nan_fill_opacity=0.4,
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f"Nombre de {view_type}s"
).add_to(m)

st.title(f"Carte interactive des {view_type.lower()}s de taxi {taxi_type.lower()} à New York")
st_folium(m, width=700, height=500)