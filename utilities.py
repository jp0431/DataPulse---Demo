import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import csv
import chardet
from visualization import render_charts_for_col, gen_Corr
from insights import dataset_score
def detect_variable_type(series):

    if series.dtype == "object":
        return "categorical"

    nunique = series.nunique()

    # ordinal/discreta
    if nunique <= 15:
        return "ordinal"

    return "numerical"

def metric_card(title, value, icon, tema):
    st.markdown(
        f"""
        <div style="
            padding: 15px;
            border-radius: 12px;
            background-color: {tema['card_bg']};
            border: 1px solid {tema['card_border']};
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
            margin-bottom: 10px;
        ">
            <div style="font-size: 28px; margin-bottom: 5px;">{icon}</div>
            <h4 style="margin: 0; font-size: 14px; color: {tema['text']}; opacity: 0.8;">{title}</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 0; color: {tema['accent']};">{value}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_tab_visualizaciones(chart_plan, data):
    chart_items = list(chart_plan.items())
    for i in range(0, len(chart_items), 3):
        cols = st.columns(3)
        for j, col_widget in enumerate(cols):
            if i + j < len(chart_items):
                col, charts_for_col = chart_items[i + j]
                with col_widget:
                    st.markdown(f"### {col}")
                    render_charts_for_col(col, charts_for_col, data)

def render_tab_timeline(analisis, data):
    date_cols = [" "] + analisis["Columnas fecha"]
            #date_cols = data[cols_fecha].columns.tolist()
    cols_num = [" "] + analisis["Columnas numericas"].to_list()
    selected_date_col = st.selectbox("Selecciona la columna de fecha", date_cols)
    selected_num_col = st.selectbox("Selecciona la columna numérica para timeline", cols_num)
            
    if selected_date_col != " " and selected_num_col != " ":
        fig = render_charts_for_col(selected_date_col, ["TimeLine"], data, num_col=selected_num_col)
        st.download_button("Descargar grafico",fig.to_image(format="png"), file_name="timeline.png", mime="image/png", disabled=True)
    else: st.warning("Selecciona una columna de fecha y una numérica para mostrar la línea de tiempo")
def render_tab_insights(insights):
    st.subheader("💡 Diagnóstico Automático de Calidad")
    
    # Si las etiquetas están homologadas (ej: "🔴 CRITICO", "🟡 IMPORTANTE")
    for severity, items in insights.items():
        if len(items) == 0:
            continue
            
        with st.expander(f"{severity} ({len(items)} detectados)"):
            for msg in items:
                # Aplicamos el contenedor visual según el nivel
                if "Critica" in severity:
                    st.error(msg, icon="🚨")
                elif "Importante" in severity:
                    st.warning(msg, icon="⚠️")
                else:
                    st.info(msg, icon="ℹ️")

def render_tab_correlaciones(data):
    num_cols = data.select_dtypes(include="number").columns.tolist()
    cols = st.multiselect("Selecciona columnas numéricas", sorted(num_cols))
    fig = None  
    descarga = False
    if len(cols) == 0:
        st.info("Selecciona al menos 2 columnas")
        descarga = False
    elif len(cols) == 1:
        st.warning("Selecciona 2 columnas para scatter o 3 para heatmap")
        descarga = False
    elif len(cols) == 2:
        descarga = True
        fig= gen_Corr(data[cols], cols)
        
    else:
        descarga = True
        fig = gen_Corr(data[cols].corr(), cols)
    if descarga and fig is not None:
        st.download_button("Descargar grafico",fig.to_image(format="png"), file_name="correlacion.png", mime="image/png",disabled=True)

def render_tab_dataset(data, analisis, signals):
    st.dataframe(data, width='stretch')
    st.download_button(
        "Descargar Dataset Preprocesado",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="dataset_preprocesado.csv",
        mime="text/csv",
        disabled=True
    )

    score = dataset_score(data, analisis, signals) / 10
    if score >= 7.5:
        st.success(f"Puntaje del Dataset: {score:.2f} - Excelente calidad")
    elif score >= 5.0:
        st.warning(f"Puntaje del Dataset: {score:.2f} - Calidad aceptable")
    else:
        st.error(f"Puntaje del Dataset: {score:.2f} - Calidad deficiente")