import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
from datetime import date

zones = pd.read_csv("../Data/taxi_zone_lookup.csv")
taxi_zones = gpd.read_file('../Data/taxi_zones_final.shp')
yellow_pickup_counts = pd.read_parquet('../Data/yellow_pickup_counts.parquet')
yellow_dropoff_counts = pd.read_parquet('../Data/yellow_dropoff_counts.parquet')
green_pickup_counts = pd.read_parquet('../Data/green_pickup_counts.parquet')
green_dropoff_counts = pd.read_parquet('../Data/green_dropoff_counts.parquet')

yellow_pickup_counts['date'] = pd.to_datetime(yellow_pickup_counts['date'])
yellow_dropoff_counts['date'] = pd.to_datetime(yellow_dropoff_counts['date'])
green_pickup_counts['date'] = pd.to_datetime(green_pickup_counts['date'])
green_dropoff_counts['date'] = pd.to_datetime(green_dropoff_counts['date'])

yellow_zones_ids = zones[zones['Borough'] == 'Manhattan']['LocationID'].values

option = st.selectbox("Choisissez l'analyse :", ["Taxis Jaunes", "Taxis Verts", "Empiètements des taxis verts"])
view_type = st.radio("Choisissez la vue :", ["Pickup", "Dropoff"])

selected_date = st.date_input(
    "Choisissez une date :",
    min_value=min(yellow_pickup_counts['date'].min(), green_pickup_counts['date'].min()),
    max_value=max(yellow_pickup_counts['date'].max(), green_pickup_counts['date'].max())
)

if option == "Taxis Jaunes":
    data_source = yellow_pickup_counts if view_type == "Pickup" else yellow_dropoff_counts
elif option == "Taxis Verts":
    data_source = green_pickup_counts if view_type == "Pickup" else green_dropoff_counts
elif option == "Empiètements des taxis verts":
    data_source = green_pickup_counts[
        (green_pickup_counts['date'] == pd.Timestamp(selected_date)) & 
        (green_pickup_counts['LocationID'].isin(yellow_zones_ids))
    ]

filtered_data = data_source[data_source['date'] == pd.Timestamp(selected_date)]

m = folium.Map([40.7, -74], zoom_start=10, tiles="cartodbpositron")

fill_color = "Greens" if option == "Empiètements des taxis verts" else "YlOrRd" if option == "Taxis Jaunes" else "GnBu"

folium.Choropleth(
    geo_data=taxi_zones,
    name=option,
    data=filtered_data,
    columns=["LocationID", "count"],
    key_on="feature.properties.OBJECTID",
    fill_color=fill_color,
    fill_opacity=0.7,
    line_opacity=0.2,
    nan_fill_color="transparent",
    legend_name=f"Nombre de {view_type.lower()}s" if option != "Empiètements des taxis verts" else "Empiètements des taxis verts"
).add_to(m)

folium.features.GeoJson(
    taxi_zones,
    name="Zones",
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Zone", "OBJECTID"],
        aliases=["Zone :", "ID de la zone :"],
        localize=True
    ),
    style_function=lambda x: {
        'fillOpacity': 0,
        'color': 'transparent',
        'weight': 0
    }
).add_to(m)

st.title(f"Carte interactive - {option}")
st_folium(m, width=700, height=500)