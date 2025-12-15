# ------------------------------------------------------------
# Nombre: Omariel Gonzalez
# Curso: INGE3016L20
# Profesor: Elio Ramos
# Fecha: 17 de noviembre
#
# Descripción del programa:
# La app utiliza Streamlit para mostrar datos en tiempo
# real de terremotos mediante la librería QuakeFeed.
# El programa permite enseñar los eventos por periodo
# de tiempo y zona geográfica (Puerto Rico o Mundo).
#
# Se generan visualizaciones que incluyen:
# - Mapa con terremotos localizados geográficamente,
#   donde el color y el tamaño representan la magnitud.
# - Histogramas de magnitudes y profundidades.
# - Una tabla con los eventos registrados y su clasificación.
# ------------------------------------------------------------


import streamlit as st
from quakefeeds import QuakeFeed
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Terremotos", layout="wide")

token_id = "pk.eyJ1IjoibWVjb2JpIiwiYSI6IjU4YzVlOGQ2YjEzYjE3NTcxOTExZTI2OWY3Y2Y1ZGYxIn0.LUg7xQhGH2uf3zA57szCyw"
px.set_mapbox_access_token(token_id)

def clasifica_mag(m):
    if m < 2: return "micro"
    if 2 <= m <= 3.9: return "menor"
    if 4 <= m <= 4.9: return "ligero"
    if 5 <= m <= 5.9: return "moderado"
    if 6 <= m <= 6.9: return "fuerte"
    if 7 <= m <= 7.9: return "mayor"
    if 8 <= m <= 9.9: return "épico"
    return "legendario"

def generaTabla(severidad, periodo):
    feed = QuakeFeed(severidad, periodo)

    lon = [feed.location(i)[0] for i in range(len(feed))]
    lat = [feed.location(i)[1] for i in range(len(feed))]
    fecha = list(feed.event_times)
    prof = list(feed.depths)
    loc = list(feed.places)
    mag = list(feed.magnitudes)

    df = pd.DataFrame({"fecha": fecha, "lon": lon, "lat": lat, "loc": loc, "mag": mag, "prof": prof})

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
    df["prof"] = pd.to_numeric(df["prof"], errors="coerce")
    df = df.dropna(subset=["lat", "lon", "mag", "prof"]).reset_index(drop=True)

    df = df[(df["mag"] >= 0) & (df["prof"] >= 0)].reset_index(drop=True)

    df["clasificación"] = df["mag"].apply(clasifica_mag)

    return df

def filtra_zona(df, zona):
    if zona == "Puerto Rico":
        return df[(df["lat"].between(16.5, 19.0)) & (df["lon"].between(-68.5, -64.0))].reset_index(drop=True)
    return df

def generaMapa(df, zona):
    if zona == "Puerto Rico":
        center = dict(lat=18.25178, lon=-66.254512)
        zoom = 7.5
    else:
        center = dict(lat=10, lon=0)
        zoom = 1.1

    df = df.copy()
    df["size"] = np.clip(df["mag"], 0, None) + 0.5
    df = df[df["size"] >= 0].reset_index(drop=True)

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="mag",
        size="size",
        hover_name="loc",
        hover_data={"fecha": True, "mag": True, "prof": True, "lat": True, "lon": True, "clasificación": True},
        color_continuous_scale="Turbo",
        range_color=[0, 7],
        size_max=10,
        opacity=0.6,
        center=center,
        zoom=zoom,
        mapbox_style="dark",
        height=600
    )
    return fig

def hist_mag(df):
    return px.histogram(df, x="mag", nbins=40, color_discrete_sequence=["red"], title="Histograma de Magnitudes", height=400)

def hist_prof(df):
    return px.histogram(df, x="prof", nbins=40, color_discrete_sequence=["red"], title="Histograma de Profundidades", height=400)

st.sidebar.header("Controles")

sev_map = {"todos": "all", "significativo": "significant", "4.5": "4.5", "2.5": "2.5", "1.0": "1.0"}
per_map = {"mes": "month", "semana": "week", "día": "day"}

sev_label = st.sidebar.selectbox("Severidad", ["todos", "significativo", "4.5", "2.5", "1.0"], index=0)
per_label = st.sidebar.selectbox("Periodo", ["mes", "semana", "día"], index=0)
zona = st.sidebar.selectbox("Zona Geográfica", ["Puerto Rico", "Mundo"], index=0)

mostrar_mapa = st.sidebar.checkbox("Mostrar mapa", value=True)
mostrar_tabla = st.sidebar.checkbox("Mostrar tabla con eventos", value=False)

n_eventos = 5
if mostrar_tabla:
    n_eventos = st.sidebar.slider("Cantidad de eventos", min_value=5, max_value=20, value=5, step=1)

st.sidebar.markdown("---")
st.sidebar.write("Aplicación desarrollada por:")
st.sidebar.write("Omariel Gonzalez")
st.sidebar.write("INGE3016L20")
st.sidebar.write("Profesor: Elio Ramos")
st.sidebar.write("Fecha: 17 de noviembre")
st.sidebar.write("Universidad de Puerto Rico en Humacao")

df = filtra_zona(generaTabla(sev_map[sev_label], per_map[per_label]), zona)

st.title("Datos en Tiempo Real de los Terremotos en Puerto Rico y en el Mundo")

st.write(f"Fecha de petición: {datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')}")
st.write(f"Cantidad de eventos: {len(df)}")

if len(df) > 0:
    st.write(f"Promedio de magnitudes: {df['mag'].mean():.2f}")
    st.write(f"Promedio de profundidades: {df['prof'].mean():.2f} km")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    st.plotly_chart(hist_mag(df), use_container_width=True)

with col2:
    st.plotly_chart(hist_prof(df), use_container_width=True)

with col3:
    if mostrar_mapa:
        st.plotly_chart(generaMapa(df, zona), use_container_width=True)

if mostrar_tabla:
    st.dataframe(df.head(n_eventos), use_container_width=True)

# Librerías utilizadas:
# - Streamlit
# - Pandas
# - Plotly
# - QuakeFeeds
# - NumPy
#
# Ejecución del programa:
# Para ejecutar la aplicación, desde la terminal se debe utilizar
# lo siguiente:
#
# streamlit run terremoto_ogonzalez.py
