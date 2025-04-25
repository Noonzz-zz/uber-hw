import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from datetime import datetime

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)


selected_date = st.date_input("Pick a date", value=data[DATE_COLUMN].dt.date.iloc[0])
data = data[data[DATE_COLUMN].dt.date == selected_date]


selected_hour = st.selectbox('Select hour of day', range(24), index=17)
filtered_data = data[data[DATE_COLUMN].dt.hour == selected_hour]


st.subheader(f'3D Map of pickups at {selected_hour}:00 on {selected_date}')
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=40.7128,
        longitude=-74.0060,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=filtered_data,
            get_position='[lon, lat]',
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))


st.subheader('Pickups by hour (Plotly)')
hour_counts = data[DATE_COLUMN].dt.hour.value_counts().sort_index()
fig = px.bar(x=hour_counts.index, y=hour_counts.values, labels={'x': 'Hour', 'y': 'Number of pickups'})
st.plotly_chart(fig)


if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Click to increase the count"):
    st.session_state.count += 1

st.write(f"This Page has run: {st.session_state.count} times")
