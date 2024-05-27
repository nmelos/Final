import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
from PIL import Image
import plotly.graph_objects as go
import os
import warnings
import sys
import platform
import sqlite3
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ElectroDunas", page_icon=":bar_chart:",layout="wide")

#st.title(" :bar_chart: ElectroDunas")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

#os.chdir('C:/Nelson/ANDES/Bimestre 8/Proyecto aplicado en analítica de datos/Semana 8/Prueba/CargaTG')
con = sqlite3.connect('Clientes.db')

#print(df)

## Logo Tittle
image = Image.open('ElectroDunasLogo.jpg')
col1, col2 = st.columns((2))
with col1:
    st.image(image, width=600) 
with col2:
    st.title("")

## create new column fecha_ymd
#df['fecha_ymd'] = df.iloc[:, 1].str[:10]
#SELECT DATE(MAX(Fecha), '-5 month') AS FI, DATE(MAX(Fecha)) AS FM FROM ClientesF
Fechas = pd.read_sql_query ('SELECT * FROM V_Fechas;', con)

#print(Fechas)

col1, col2 = st.columns((2))
#df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"])

# Getting the min and max fecha_ymd 
#startDate = pd.to_datetime(df["fecha_ymd"]).min()
#endDate = pd.to_datetime(df["fecha_ymd"]).max()
startDate = pd.to_datetime(Fechas["FI"]).min()
endDate = pd.to_datetime(Fechas["FM"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Fecha Inicio", startDate))
    s=date1.strftime("%Y-%m-%d")
with col2:
    date2 = pd.to_datetime(st.date_input("Fecha Fin", endDate))
    e=date2.strftime("%Y-%m-%d")


# Filters
st.sidebar.header("Escoge tu filtro: ")

# Choose for Sector
query = 'SELECT DISTINCT SectorD, ClientesD FROM Clientes WHERE Time >= "20:00:00" AND FechaC >= ? AND FechaC <= ? ORDER BY ClientesD, SectorD;'
params = [s, e]
SectorCliente = pd.read_sql_query (query, con, params=params)
#sector = st.sidebar.multiselect("Escoge el Sector", sector)
sector = st.sidebar.multiselect("Escoge el Sector", SectorCliente["SectorD"].unique())
if not sector:
    SectorCliente2 = SectorCliente.copy()
else:
    SectorCliente2 = SectorCliente[SectorCliente["SectorD"].isin(sector)]

# Choose for Cliente
cliente = st.sidebar.multiselect("Escoge el Cliente", SectorCliente2["ClientesD"].unique())
if not cliente:
    SectorCliente3 = SectorCliente2.copy()
else:
    SectorCliente3 = SectorCliente2[SectorCliente2["ClientesD"].isin(cliente)]


# Filter the data based on sector and cliente
if not sector and not cliente:
    query = 'SELECT "index", Fecha, SectorD, ClientesD, Cluster, Active_energy, FechaC, Anomalo FROM Clientes WHERE Time >= "20:00:00" AND FechaC >= ? AND FechaC <= ?;'
    params = [s, e]
    df = pd.read_sql_query (query, con, params=params)
    #df['fecha_ymd'] = df.iloc[:, 1].str[:10]
    #df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"]) 
    filtered_df = df
elif sector and not cliente:
    query = 'SELECT "index", Fecha, SectorD, ClientesD, Cluster, Active_energy, FechaC, Anomalo FROM Clientes WHERE Time >= "20:00:00" AND FechaC >= ? AND FechaC <= ? AND SectorD IN ({});'.format(', '.join(["'{}'".format(v) for v in sector]))      
    params = [s, e] 
    #df = pd.read_sql_query (query, con, params=params)
    #df['fecha_ymd'] = df.iloc[:, 1].str[:10]
    df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"]) 
    filtered_df = df
    #filtered_df = df[df["SectorD"].isin(sector)]
elif not sector and cliente:
    query = 'SELECT "index", Fecha, SectorD, ClientesD, Cluster, Active_energy, FechaC, Anomalo FROM Clientes WHERE Time >= "20:00:00" AND FechaC >= ? AND FechaC <= ? AND ClientesD IN ({});'.format(', '.join(["'{}'".format(v) for v in cliente]))      
    params = [s, e] 
    df = pd.read_sql_query (query, con, params=params)
    #df['fecha_ymd'] = df.iloc[:, 1].str[:10]
    #df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"]) 
    filtered_df = df
    #filtered_df = df[df["ClientesD"].isin(cliente)]
else:
    query = 'SELECT "index", Fecha, SectorD, ClientesD, Cluster, Active_energy, FechaC, Anomalo FROM Clientes WHERE Time >= "20:00:00" AND FechaC >= ? AND FechaC <= ? AND SectorD IN ({});'.format(', '.join(["'{}'".format(v) for v in sector]))      
    params = [s, e] 
    df = pd.read_sql_query (query, con, params=params)
    filtered_df = df
    #df['fecha_ymd'] = df.iloc[:, 1].str[:10]
    #df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"]) 
    #filtered_df = df[df["SectorD"].isin(sector)]
    filtered_df = filtered_df[filtered_df["ClientesD"].isin(cliente)]
    
    
df['fecha_ymd'] = df.iloc[:, 1].str[:10]
df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"])
    
cluster_df = filtered_df.groupby(by = ["Cluster"], as_index = False)["Active_energy"].sum()

# ClusterHistogram - SectorDonut -- Graphics
with col1:
    col1.metric(label="Total clientes", value=filtered_df["ClientesD"].nunique())
    col1.metric(label="Vr máximo consumo por cliente", value=filtered_df["Active_energy"].max())
    
    st.subheader("Clusters o grupos de clientes")
    st.caption("Información de consumo de energia por cluster o grupos de clientes")
    fig = px.bar(cluster_df, x = "Cluster", y = "Active_energy", text = ['${:,.2f}'.format(x) for x in cluster_df["Active_energy"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    col2.metric(label="Total registros de consumos", value=len(filtered_df))
    col2.metric(label="Vr promedio de consumo por cliente", value=filtered_df["Active_energy"].mean())

    st.subheader("Información de Sectores")
    st.caption("Porcentaje de consumo de energia por sector")
    fig = px.pie(filtered_df, values = "Active_energy", names = "SectorD", hole = 0.5)
    fig.update_traces(text = filtered_df["SectorD"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))

# ClusterHistogram - SectorDonut -- DataGrids
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Datos de Clusters"):
        st.write(cluster_df.style.background_gradient(cmap="Blues"))
        csv = cluster_df.to_csv(index = False).encode('utf-8')
        st.download_button("Descargar Datos", data = csv, file_name = "Cluster.csv", mime = "text/csv",
                            help = 'Click para descargar datos en formato CSV')

with cl2:
    with st.expander("Datos de Sectores"):
        sector = filtered_df.groupby(by = "SectorD", as_index = False)["Active_energy"].sum()
        st.write(sector.style.background_gradient(cmap="Oranges"))
        csv = sector.to_csv(index = False).encode('utf-8')
        st.download_button("Descargar Datos", data = csv, file_name = "Sector.csv", mime = "text/csv",
                        help = 'Click para descargar datos en formato CSV')


# TimeSeries        
filtered_df["year_month"] = filtered_df["fecha_ymd"].dt.to_period("M")
st.subheader('Análisis de Consumos')
st.caption("Información de histórico de consumo de energía de los clientes por año:mes")
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["year_month"].dt.strftime("%Y : %m"))["Active_energy"].sum()).reset_index()
fig2 = px.line(linechart, x = "year_month", y="Active_energy", labels = {"Active_energy": "kWh"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("Datos de Consumos:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Descargar Datos', data = csv, file_name = "Consumos.csv", mime ='text/csv') 


# Treem based on Sector, Cluster, and Cliente
st.subheader("Relación de Sectores - Clusters - Clientes")
st.caption("Información de Sectores productivos con sus respectivos clusters y clientes, generado con modelo de aprendizaje no supervisado")
fig3 = px.treemap(filtered_df, path = ["SectorD","Cluster","ClientesD"], values = "Active_energy", hover_data = ["Active_energy"], color = "ClientesD")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)


# Anomalies Graphic
st.subheader('Análisis de Anomalías')
st.caption("Información de registro de consumos de energía con y sin anomalías, generado con modelo de aprendizaje no supervisado")

df_tmp = filtered_df[filtered_df.iloc[:, 7] == 1].copy()
df_anom = df_tmp.copy()
df_agg_anom = df_anom.groupby('fecha_ymd')['Active_energy'].sum().reset_index()

df_tmp = filtered_df[filtered_df.iloc[:, 7] == 0].copy()
df_no_anom = df_tmp.copy()
df_agg_no_anom = df_no_anom.groupby('fecha_ymd')['Active_energy'].sum().reset_index()

fig4 = go.Figure()

fig4.add_trace(go.Bar(
    x=df_agg_no_anom['fecha_ymd'],
    y=df_agg_no_anom['Active_energy'],
    name='Consumos sin anomalías',
    marker_color='blue'
))

fig4.add_trace(go.Bar(
    x=df_agg_anom['fecha_ymd'],
    y=df_agg_anom['Active_energy'],
    name='Consumos con anomalías',
    marker_color='red',
    marker={"opacity": 0.4}
))

fig4.update_layout(
    autosize=False,
    height=500, 
    width = 1200,
    #title='Información de consumos con anomalías',
    xaxis_title='Fecha',
    yaxis_title='Consumo',
    barmode='overlay'  # superponer las barras
)

st.plotly_chart(fig4)


# HorizontalHistograms for Sector, and Cliente
st.subheader("Detalles de Sectores")
st.caption("Información de consumo de energía por sectores productivos")
fig5 = px.bar(filtered_df, x = "Active_energy", y = "SectorD", orientation='h' )
st.plotly_chart(fig5, use_container_width=True)

st.subheader("Detalles de Clientes")
st.caption("Información de consumo de energía por clientes")
fig6 = px.bar(filtered_df, x = "Active_energy", y = "ClientesD", orientation='h' )
st.plotly_chart(fig6, use_container_width=True)