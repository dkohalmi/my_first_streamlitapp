import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

# Read and cache the dataframe:
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df
df_raw = load_data(path="./data/raw/renewable_power_plants_CH.csv")
df = deepcopy(df_raw)

#electrical_capacity:Installed electrical capacity in MW
#commissioning_date:Description: Commissioning date
#contract_period_end:Description: End of subsidy contract
#tariff:Tariff in CHF for 2016
#production:Yearly production in MWh

# Read and cache the geojson file:
@st.cache_data
def load_geojson(path):
    with open(path) as json_file:
        data_geojson =json.load(json_file)
    return data_geojson
geojson_raw = load_geojson(path="./data/raw/georef-switzerland-kanton.geojson")
geojson = deepcopy(geojson_raw)

#Clean the dataframe (change 'ZH' ---> to Zurich
cantons_dict = {
'TG':'Thurgau',
'GR':'Graubünden',
'LU':'Luzern',
'BE':'Bern',
'VS':'Valais',
'BL':'Basel-Landschaft',
'SO':'Solothurn',
'VD':'Vaud',
'SH':'Schaffhausen',
'ZH':'Zürich',
'AG':'Aargau',
'UR':'Uri',
'NE':'Neuchâtel',
'TI':'Ticino',
'SG':'St. Gallen',
'GE':'Genève',
'GL':'Glarus',
'JU':'Jura',
'ZG':'Zug',
'OW':'Obwalden',
'FR':'Fribourg',
'SZ':'Schwyz',
'AR':'Appenzell Ausserrhoden',
'AI':'Appenzell Innerrhoden',
'NW':'Nidwalden',
'BS':'Basel-Stadt'}

# Rewrite the name of the cantons:
df['canton']=df['canton'].map(cantons_dict)

# Production / Electrical capacity in different cantons, different sources
df_productionsum_sources=df.groupby(['energy_source_level_2','canton'])['production'].sum().reset_index()
df_capacitysum_sources=df.groupby(['energy_source_level_2','canton'])['electrical_capacity'].sum().reset_index()

# Number of power plants in different cantons, different sources
df_plants_count=df.groupby(['canton'])['electrical_capacity'].count().reset_index()
df_plants_count_sources=df.groupby(['energy_source_level_2','canton'])['electrical_capacity'].count().reset_index()

# Production / Electrical capacity in different cantons, all sources together
df_productionsum_all=df.groupby(['canton'])['production'].sum().reset_index()
df_capacitysum_all=df.groupby(['canton'])['electrical_capacity'].sum().reset_index()

# Add title and header
st.title("Renewable Energy in Switzerland")
st.write()
st.write("The charts show all renewable-energy power plants in Switzerland in the selected category supported by the feed-in-tariff KEV (Kostendeckende Einspeisevergütung.)")

# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show Original Dataframe"):
    st.subheader("All renewable-energy power plants supported by the feed-in-tariff KEV:")
    st.dataframe(data=df)


# Yearly production in MWh
st.subheader("Yearly production in MWh")

#Make columns:
first_column,second_column=st.columns([1,1])

# Widgets: selectbox
energysources1 = ["All"]+sorted(pd.unique(df['energy_source_level_2']))
energysource1 = first_column.selectbox("Choose an energy source for production:", energysources1)

# Flow control and plotting
if energysource1 == "All":
    reduced_df = df_productionsum_all
else:
    reduced_df = df_productionsum_sources[df_productionsum_sources['energy_source_level_2'] ==energysource1]



plotly_map = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=reduced_df.canton,
                                    featureidkey="properties.kan_name",
                                    z=reduced_df.production,
                                    colorscale="Viridis",
                                    marker_opacity=0.5, marker_line_width=0))

plotly_map.update_layout(mapbox_style="carto-positron",
                        margin={"r":0,"t":0,"l":0,"b":0},
                  mapbox_zoom=6, mapbox_center = {"lat":46.8182 , "lon":8.2275 })

st.plotly_chart(plotly_map)


#Installed electrical capacity in MW
st.subheader("Installed electrical capacity in MW")

# Widgets: selectbox
energysources2 = ["All"]+sorted(pd.unique(df['energy_source_level_2']))
energysource2 = st.selectbox("Choose an energy source for capacity:", energysources2)

# Flow control and plotting
if energysource2 == "All":
    reduced_df = df_capacitysum_all
else:
    reduced_df = df_capacitysum_sources[df_capacitysum_sources['energy_source_level_2'] ==energysource2]


plotly_map = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=reduced_df.canton,
                                    featureidkey="properties.kan_name",
                                    z=reduced_df.electrical_capacity,
                                    colorscale="Viridis",
                                    marker_opacity=0.5, marker_line_width=0))

plotly_map.update_layout(mapbox_style="carto-positron",
                        margin={"r":0,"t":0,"l":0,"b":0},
                  mapbox_zoom=6, mapbox_center = {"lat":46.8182 , "lon":8.2275 })

st.plotly_chart(plotly_map)

#Number of power plants:

st.subheader("The number of installed power plants producing renewable energy")

# Widgets: selectbox
energysources3 = ["All"]+sorted(pd.unique(df['energy_source_level_2']))
energysource3 = st.selectbox("Choose an energy source for the number of power plants:", energysources3)

# Flow control and plotting
if energysource3 == "All":
    reduced_df = df_plants_count
else:
    reduced_df = df_plants_count_sources[df_plants_count_sources['energy_source_level_2'] ==energysource3]


plotly_map = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=reduced_df.canton,
                                    featureidkey="properties.kan_name",
                                    z=reduced_df.electrical_capacity,
                                    colorscale="Viridis",
                                    marker_opacity=0.5, marker_line_width=0))

plotly_map.update_layout(mapbox_style="carto-positron",
                        margin={"r":0,"t":0,"l":0,"b":0},
                  mapbox_zoom=6, mapbox_center = {"lat":46.8182 , "lon":8.2275 })

st.plotly_chart(plotly_map)


# Barplot:
#st.subheader("The yearly production in MWh")
# Flow control and plotting

fig=go.Figure(
    data=[
        go.Bar(x=df_productionsum_sources['canton'],y=df_productionsum_sources[df_productionsum_sources['energy_source_level_2']=='Bioenergy']['production'],name='Bioenergy'),
        go.Bar(x=df_productionsum_sources['canton'],y=df_productionsum_sources[df_productionsum_sources['energy_source_level_2']=='Hydro']['production'],name='Hydro'),
        go.Bar(x=df_productionsum_sources['canton'],y=df_productionsum_sources[df_productionsum_sources['energy_source_level_2']=='Solar']['production'],name='Solar'),
        go.Bar(x=df_productionsum_sources['canton'],y=df_productionsum_sources[df_productionsum_sources['energy_source_level_2']=='Wind']['production'],name='Wind'),
    ],layout={'barmode':'stack','title': {'text': "The yearly production in MWh", "font": {"size": 24}}})
st.plotly_chart(fig)


# We can write stuff
url = "https://open-power-system-data.org/"
st.write("Data Source:", url)
# "This works too:", url
