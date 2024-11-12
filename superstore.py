 # Importation des modules nécessaires
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(page_title='Analyse du Marché',page_icon=":bar_chart",layout="wide")

st.title(" :bar_chart: Mon Dash bord")
# st.markdown("<style>div.block-container{padding-top:1rem;}</style>",unsafe_allow_html=True)

# Chargement du fichier
fl = st.file_uploader(":file_folder: Veuillez charger le fichier",type = (["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename,encoding='ISO-8859-1', delimiter=";")
else:
    os.chdir(r"C:\Users\X1 Carbon\Desktop\ABLO'S FOLDER\ONLINE COURSE-SQL-ABLO\PYTHON\PYTHON\STREAMLIT\DASH_BORD")
    df = pd.read_csv("superstore.csv",encoding='ISO-8859-1',delimiter=";")

col1, col2 = st.columns((2))

# Conversion de la variable date de commande en date
df["Order Date"] = pd.to_datetime(df["Order Date"],format='%d/%m/%Y')

# Donner la date min et max

datedebut = pd.to_datetime(df["Order Date"],format= '%d/%m/%Y').min()
datefin = pd.to_datetime(df["Order Date"],format='%d/%m/%Y').max()

# Selectionne des dates
with col1:
    date1 = pd.to_datetime(st.date_input("Date de début",value=datedebut),format='%d/%m/%Y')
with col2:
    date2 = pd.to_datetime(st.date_input("Date de fin",value=datefin),format='%d/%m/%Y')
df = df[(df["Order Date"] >= date1) & (df["Order Date"]<= date2)].copy()

# Selection des filtres régions
st.sidebar.header("Choissez votre filtre : ")
region = st.sidebar.multiselect("Selectionnez vos régions", df["Region"].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]
# Selection des filtres régions
etat = st.sidebar.multiselect("Selectionnez votre Etat : ", df2["State"].unique())
if not etat:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(etat)]
# Selectionne de la ville 
ville = st.sidebar.multiselect("Selectionnez votre ville : ", df3["City"].unique())

# Filtrer les données selon l'état, la region et la ville
if not region and not etat and not ville:
    filtre_df = df
elif not etat and not ville:
    filtre_df = df[df["Region"].isin(region)]
elif not region and not ville:
    filtre_df = df[df["State"].isin(etat)]
elif etat and ville:
    filtre_df = df3[(df["State"].isin(etat)) & (df["City"].isin(ville))]
elif region and ville:
    filtre_df = df3[(df["Region"].isin(region)) & (df["City"].isin(ville))]
elif region and etat:
    filtre_df = df3[(df["Region"].isin(region)) & (df["State"].isin(etat))]
elif ville:
    filtre_df = df3[df3["City"].isin(ville)]
else:
    filtre_df = df3[(df3["Region"].isin(region)) & (df3["State"].isin(etat)) & (df3["City"].isin(ville))]


category_df = filtre_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()
category_df["Sales"] = pd.to_numeric(category_df["Sales"])
with col1:
    st.subheader("Vente par catégorie")
    fig = px.bar(category_df, x = "Category", y = "Sales", text=[f'${x:,.2f}' for x in category_df["Sales"]], 
    template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height =200)

# 
with col2:
    st.subheader("Vente par région")
    fig = px.pie(filtre_df, values= "Sales", names = "Region",hole=0.5)
    fig.update_traces(text = filtre_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Voir les données de la catégorie"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode("utf-8")
        st.download_button("Télécharger le dataset",data = csv,file_name="categorie.csv",mime = "text/csv",
        help="Cliquer pour télécharger la data comme un fichier pdf")
with cl2:
    with st.expander("Voir les données de la région"):
        region = filtre_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(category_df.style.background_gradient(cmap="Oranges"))
        csv = category_df.to_csv(index = False).encode("utf-8")
        st.download_button("Télécharger le dataset",data = csv,file_name="region.csv",mime = "text/csv",
        help="Cliquer pour télécharger la data comme un fichier pdf")

filtre_df["month_year"] = filtre_df["Order Date"].dt.to_period("M") 
st.subheader("Analyse des séries temporelles")

line_chart = pd.DataFrame(filtre_df.groupby(by=filtre_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(line_chart, x= "month_year", y = "Sales",labels={"Sales":"Ventes"},
height=500,width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Visualisation des séries temporelles") :
    st.write(line_chart.T.style.background_gradient(cmap = "Blues"))
    csv = line_chart.to_csv(index=False).encode("utf-8")
    st.download_button("Télécharger les données", data = csv, file_name="serietemporelle.csv",mime = "text/csv")

# Création 
st.subheader("Visualisation hierarchique de la ventes avec TreeMap")
fig3 = px.treemap(filtre_df,path=["Region","Category", "Sub-Category"],
values = "Sales", hover_data=["Sales"], color = "Sub-Category")
fig3.update_layout(width = 800,height =650)
st.plotly_chart(fig3,use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment du marché par ventes")
    fig = px.pie(filtre_df, values = "Sales", names = "Segment", template="plotly_dark")
    fig.update_traces(text = filtre_df["Segment"],textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Segment de la catégorie par ventes")
    fig = px.pie(filtre_df, values = "Sales", names = "Category", template="gridon")
    fig.update_traces(text = filtre_df["Category"],textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Le mois selon la catégorie de vente")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Mois par sous catégorie de table")
    filtre_df["month"] = filtre_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data = filtre_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_year.style.background_gradient(cmap = "Blues"))
data1 = px.scatter(filtre_df, x = "Sales", y = "Profit", size = "Quantity")
data1["layout"].update(title = "Relation entre la vente et le prix",
                        titlefont = dict(size = 20), xaxis = dict(title = "Sales", titlefont = dict(size=19)),
                        yaxis = dict(title = "Profit", titlefont = dict(size= 19)))
st.plotly_chart(data1, use_container_width=True)