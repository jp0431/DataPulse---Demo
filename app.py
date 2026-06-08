from utilities import st, render_tab_visualizaciones, render_tab_timeline, render_tab_insights, render_tab_correlaciones, render_tab_dataset
from core.loader import exportar_html, clean_columns, exportar, load_file
from analisys import basic_analisis
from preprocessing import preprocessing_data
from core.scorer import gen_scores
from core.gen_charts import gen_charts
from insights import gen_insights, extract_signals, generate_summary, build_report
def begin(data):
    # 3. Análisis general
    analisis = basic_analisis(data)
    # 4. Preprocesamiento
    data, imputation_log = preprocessing_data(data)
    # 5. Selección de columnas relevantes
    top_num, top_cat = gen_scores(data)

    # 6. Plan de gráficos
    chart_plan, charts = gen_charts(top_num, top_cat, data)

    # 7. Insights
    insights = gen_insights(data, analisis, imputation_log)

    # 8. Señales globales
    signals = extract_signals(data)

    # 9. Resumen ejecutivo
    summary = generate_summary(
        data,
        insights["🔴 Critica"],
        insights["🟡 Importante"],
        signals
    )
    return data, analisis, insights, chart_plan, signals, summary
# ============================================================
# CONFIGURACIÓN
# ============================================================

LOGO = "IMG/grafico-de-barras.png"

st.logo(LOGO)
st.set_page_config(page_title="DataPulse DEMO",page_icon=LOGO, layout="wide")






st.markdown("""
    <style>
    /* Estilizar la zona de arrastrar archivos */
    .stFileUploader {
        border: 2px dashed #7F77DD !important;
        border-radius: 10px;
        background-color: #0e1117;
    }
    </style>
""", unsafe_allow_html=True)
# st.title("Análisis exploratorio de datos automático")
# st.markdown("""
# <div style='text-align:left; padding:20px 0;'>
#     <p style='color:gray; font-size:30px;'>
#         Exploración automática de datos con visualizaciones inteligentes
#     </p>
# </div>
# """, unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: left; padding: 10px 0 20px 0;'>
        <h1 style='
            font-size: 42px; 
            font-weight: 800; 
            color: #7F77DD; 
            margin-bottom: 5px;
            letter-spacing: -1px;
        '>
            Business Dataset Analyzer <span style='font-size: 20px; font-weight: 400; color: gray; vertical-align: middle;'></span>
        </h1>
        <p style='
            color: var(--text-color); 
            font-size: 18px; 
            opacity: 0.7;
            margin: 0;
        '>
            Transforma tus datos crudos en insights accionables al instante. Sin escribir una sola línea de código.
        </p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# VARIABLES DE ESTADO
# ============================================================
archivo_cargado = None
cargado = False
data = None
analisis = None
summary = None
insights = None
signals = None
chart_plan = None


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("Arrastra un archivo CSV")

    archivo_cargado = st.file_uploader("Selecciona tu archivo", type=["csv"])

    if archivo_cargado:
        st.success("¡Archivo cargado con éxito!")
        cargado = True

        with st.spinner("Procesando dataset..."):

            data = load_file(archivo_cargado)
            data, analisis, insights, chart_plan, signals, summary = begin(data)




# ============================================================
# CONTENIDO PRINCIPAL
# ============================================================
if cargado:
    with st.sidebar:
        st.markdown("---")
        st.title("⚙️ Panel de Control")
        st.markdown("### 📋 Configuración del Análisis")
        st.header("Selector de columnas")
        cols = st.multiselect("Deselecciona las columnas que no quieres analizar", options=data.columns, default=data.columns.tolist())
        data = data[cols]
        if len(cols) == 0:
            st.warning("Selecciona al menos una columna para analizar")
            st.stop()
        else:
            data, analisis, insights, chart_plan, signals, summary = begin(data)
        # Exportar reporte
        st.markdown("---")
        st.markdown("### 📥 Exportar Resultados")
        st.warning("⚠️ Exportación bloqueada en la versión DEMO.")
        st.link_button(
            "🚀 Desbloquear Reportes Completos (Pago Único)",
            url="https://jaumeps.gumroad.com/l/pxrqic", # Enlace a Gumroad 
            use_container_width=True,
            type="primary" # Esto lo pintará con tu color morado (#7F77DD) para captar atención
        )
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(
                "Exportar Reporte en TXT",
                data="Exportar en TXT no esta disponible en la versión DEMO",
                file_name="reporte_eda.txt",
                mime="text/plain",
            )
        with col_btn2:
            st.download_button(
                "Exportar Reporte en HTML",
                data="Exportar en HTML no esta disponible en la versión DEMO",
                file_name="reporte_eda.html",
                mime="text/html",
            )

        
    # ----------------------------
    # MÉTRICAS
    # ----------------------------
    st.header("Información del Dataset")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.metric("Filas", analisis["Filas"])
    with c2: st.metric("Columnas", analisis["Columnas"])
    with c3: st.metric("Nulos", f"{analisis['Porcentaje nulos']:.2f}%")
    with c4: st.metric("Numéricas", analisis["Número Columnas numericas"])
    with c5: st.metric("Categóricas", analisis["Número Columnas categoricas"])
    with c6: st.metric("Fecha", analisis["Número Columnas fecha"])

    # ----------------------------
    # RESUMEN EJECUTIVO
    # ----------------------------
    st.markdown("## Resumen ejecutivo")
    st.info(summary)

    # ----------------------------
    # TABS
    # ----------------------------
    tiene_fechas = analisis["Número Columnas fecha"] > 0
    tabs_labels = ["📊 Visualizaciones"]
    if tiene_fechas:
        tabs_labels.append("📅 Linea de tiempo")
        cols_fecha = analisis["Columnas fecha"]
    tabs_labels += ["💡 Insights", "🔗 Correlaciones", "📁 Dataset"]
    tabs = st.tabs(tabs_labels)
    tab_index = iter(range(len(tabs)))
    with tabs[next(tab_index)]:
        render_tab_visualizaciones(chart_plan, data)

    if tiene_fechas:
        with tabs[next(tab_index)]:
            render_tab_timeline(analisis, data)

    with tabs[next(tab_index)]:
        render_tab_insights(insights)

    with tabs[next(tab_index)]:
        render_tab_correlaciones(data)

    with tabs[next(tab_index)]:
        render_tab_dataset(data, analisis, signals)
# Nota la coma después de col_header_btn
    col_header_btn, = st.columns(1) 

    with col_header_btn:
        st.markdown("<div style='padding-top: 25px;'></div>", unsafe_allow_html=True)
        st.link_button(
            "🛒 Obtener Licencia de por Vida",
            url="https://jaumeps.gumroad.com/l/pxrqic",
            use_container_width=True,
            type="secondary"
        )
elif not cargado:
    # Contenedor Principal Centrado y con Tarjeta de fondo sutil
    st.markdown("""
        <div style="
            text-align: center; 
            padding: 40px 30px; 
            margin-top: 20px;
            border-radius: 16px;
            background-color: var(--background-color);
            border: 1px solid rgba(127, 119, 221, 0.15);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        ">
            <!-- Header con Cohete Animado -->
            <div style="font-size: 60px; margin-bottom: 15px; animation: float 3s ease-in-out infinite;">🚀</div>
            <h1 style="
                color: #7F77DD; 
                font-size: 36px; 
                font-weight: 800; 
                margin-bottom: 10px;
                letter-spacing: -0.5px;
            ">
                Bienvenido/a a DATAPULSE
            </h1>
            <p style="
                color: var(--text-color); 
                font-size: 18px; 
                max-width: 650px; 
                margin: 0 auto 40px auto; 
                opacity: 0.85;
                line-height: 1.6;
            ">
                Transforma tus datos crudos en reportes interactivos e insights accionables al instante. 
                Sin escribir una sola línea de código.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sección de Características / Beneficios en 3 Columnas de Streamlit
    col_b1, col_b2, col_b3 = st.columns(3)

    with col_b1:
        st.markdown("""
            <div style="text-align: center; padding: 20px; border-radius: 12px; border: 1px solid rgba(127,119,221,0.1); background: rgba(127,119,221,0.03);">
                <div style="font-size: 32px; margin-bottom: 10px;">📊</div>
                <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">Gráficos Inteligentes</h4>
                <p style="margin: 0; font-size: 13px; opacity: 0.7; line-height: 1.4;">Distribuciones logarítmicas, barras de alta cardinalidad e histogramas automáticos según tu tipo de dato.</p>
            </div>
        """, unsafe_allow_html=True)

    with col_b2:
        st.markdown("""
            <div style="text-align: center; padding: 20px; border-radius: 12px; border: 1px solid rgba(127,119,221,0.1); background: rgba(127,119,221,0.03);">
                <div style="font-size: 32px; margin-bottom: 10px;">💡</div>
                <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">Auditoría de Calidad</h4>
                <p style="margin: 0; font-size: 13px; opacity: 0.7; line-height: 1.4;">Detección automática de multicolinealidad crítica, asimetrías severas y cálculo de score de salud de datos.</p>
            </div>
        """, unsafe_allow_html=True)

    with col_b3:
        st.markdown("""
            <div style="text-align: center; padding: 20px; border-radius: 12px; border: 1px solid rgba(127,119,221,0.1); background: rgba(127,119,221,0.03);">
                <div style="font-size: 32px; margin-bottom: 10px;">🛠️</div>
                <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">Preprocesamiento</h4>
                <p style="margin: 0; font-size: 13px; opacity: 0.7; line-height: 1.4;">Imputación estadística inteligente de valores nulos mediante media o mediana ponderada por outliers.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Footer de Instrucción Final Dinámico (Llamado a la Acción)
    st.markdown("""
        <div style="
            text-align: center; 
            padding: 15px; 
            border-radius: 30px; 
            background-color: rgba(127, 119, 221, 0.1); 
            max-width: 450px; 
            margin: 0 auto;
            border: 1px dashed #7F77DD;
        ">
            <span style="font-size: 14px; font-weight: 600; color: var(--text-color);">
                👈 Comienza arrastrando tu archivo <code style="color: #7F77DD; background: none; font-weight:bold;">.csv</code> o <code style="color: #7F77DD; background: none; font-weight:bold;">.xlsx</code> en el panel lateral
            </span>
        </div>
        <br> <br>
        <p style="font-size: 14px; opacity: 0.8;">
                ¿Quieres analizar archivos sin límite de tamaño y exportar reportes en HTML/TXT corporativos? 
                <a href="https://jaumeps.gumroad.com/l/pxrqic" target="_blank" style="color: #7F77DD; font-weight: bold; text-decoration: underline;">
                    Consigue la versión completa aquí (Licencia de por vida)
    """, unsafe_allow_html=True)
