from utilities import st, pd, px


# ============================================================
# PLOTTABILITY CHECK
# ============================================================
def is_plottable(series):

    # demasiados nulos
    if series.isnull().mean() > 0.7:
        return False

    # constante
    if series.nunique() <= 1:
        return False

    # ID-like
    if series.nunique() / len(series) > 0.98:
        return False

    # texto libre muy grande
    if series.dtype == "object" and series.nunique() > 80:
        return False

    return True


# ============================================================
# DETECCIÓN DE INTENCIÓN
# ============================================================
def detect_variable_type(series):

    if pd.api.types.is_numeric_dtype(series):
        return "numerical"

    nunique = series.nunique()

    if nunique <= 20:
        return "categorical"

    return "high_cardinality"


def generate_chart_intent(series):

    vtype = detect_variable_type(series)

    if vtype == "numerical":
        if abs(series.skew()) > 1:
            return ["log_distribution"]
        return ["distribution"]

    if vtype == "categorical":
        if series.nunique() <= 5:
            return ["pie"]
        return ["bar"]

    if vtype == "high_cardinality":
        return ["top_n_bar"]

    return []


def intent_to_chart(intent):

    mapping = {
        "distribution": "histogram",
        "log_distribution": "log_histogram",
        "bar": "bar",
        "top_n_bar": "top_n_bar",
        "pie": "pie"
    }

    return [mapping[i] for i in intent if i in mapping]


# ============================================================
# GENERACIÓN DEL PLAN DE GRÁFICOS
# ============================================================
def generate_chart_plan(data):

    chart_plan = {}

    for col in data.columns:

        series = data[col]

        if not is_plottable(series):
            continue

        intents = generate_chart_intent(series)
        charts = intent_to_chart(intents)

        if charts:
            chart_plan[col] = charts

    return chart_plan


# ============================================================
# RENDERIZACIÓN DE GRÁFICOS
# ============================================================
def render_charts_for_col(col, charts, data,  num_col = None):

    for chart in charts:

        # HISTOGRAM
        if chart == "histogram":
            fig = px.histogram(data, x=col, color_discrete_sequence=["#7F77DD"])
            st.plotly_chart(fig, width='stretch')

        # LOG HISTOGRAM
        elif chart == "log_histogram":
            fig = px.histogram(data, x=col, log_y=True, color_discrete_sequence=["#1D9E75"])
            st.plotly_chart(fig, width='stretch')

        # BAR
        elif chart == "bar":
            counts = data[col].value_counts().head(20)
            fig = px.bar(counts, color_discrete_sequence=["#378ADD"])
            st.plotly_chart(fig, width='stretch')

        # TOP N BAR
        elif chart == "top_n_bar":
            counts = data[col].value_counts().head(10)
            fig = px.bar(counts, color_discrete_sequence=["#378ADD"])
            st.plotly_chart(fig, width='stretch')

        # PIE
        elif chart == "pie":
            counts = data[col].value_counts().head(5).reset_index()
            counts.columns = [col, "count"]
            fig = px.pie(
                counts,
                names=col,
                values="count",
                color_discrete_sequence=[
                    "#7F77DD", "#1D9E75", "#D85A30",
                    "#378ADD", "#D4537E", "#BA7517"
                ]
            )
            st.plotly_chart(fig, width='stretch')
        # elif chart == "TimeLine":
        #     fig = px.line(data, x=col, y=num_col, color_discrete_sequence=["#7F77DD"])
        #     st.plotly_chart(fig, width='stretch')
        elif chart == "TimeLine":

            df = data.copy()

            # 1. Convertir a datetime
            df[col] = pd.to_datetime(df[col], errors="coerce", format="%Y-%m-%d")

            # 2. Eliminar filas sin fecha válida
            df = df.dropna(subset=[col, num_col])

            # 3. Ordenar por fecha
            df = df.sort_values(col)
            freq = detect_auto_agroup(df[col])
            # 4. Agrupar por semana (o "M" para mensual)
            df_grouped = df.groupby(pd.Grouper(key=col, freq=freq)).agg({num_col: "sum"}).reset_index()
            # 5. Rolling mean (suavizado)
            #df_grouped["rolling"] = df_grouped[num_col].rolling(4).mean()

            # 6. Dibujar
            fig = px.line(
                df_grouped,
                x=col,
                y=num_col,
                labels={num_col: num_col},
                color_discrete_sequence=["#7F77DD", "#1D9E75"]
            )

            fig.update_layout(
                xaxis_title="Fecha",
                yaxis_title=num_col,
                legend_title="Series",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, width='stretch')
        return fig
            # Aplicar plantilla de Plotly según el modo seleccionado
    
def detect_auto_agroup(series):
    series = pd.to_datetime(series, errors="coerce").dropna().sort_values()

    if len(series) < 2:
        return "M"  # fallback

    diffs = series.diff().dropna()
    median_diff = diffs.median()

    if median_diff <= pd.Timedelta(days=1):
        return "D"   # datos diarios
    elif median_diff <= pd.Timedelta(days=7):
        return "W"   # datos semanales
    elif median_diff <= pd.Timedelta(days=31):
        return "M"   # datos mensuales
    else:
        return "Y"   # datos anuales    
def render_charts_for_col_html(col, charts, data,  num_col = None):
    figures = []
    for chart in charts:

        # HISTOGRAM
        if chart == "histogram":
            fig = px.histogram(data, x=col, color_discrete_sequence=["#7F77DD"])
            #st.plotly_chart(fig, width='stretch')

        # LOG HISTOGRAM
        elif chart == "log_histogram":
            fig = px.histogram(data, x=col, log_y=True, color_discrete_sequence=["#1D9E75"])
            #st.plotly_chart(fig, width='stretch')

        # BAR
        elif chart == "bar":
            counts = data[col].value_counts().head(20)
            fig = px.bar(counts, color_discrete_sequence=["#378ADD"])
            #st.plotly_chart(fig, width='stretch')

        # TOP N BAR
        elif chart == "top_n_bar":
            counts = data[col].value_counts().head(10)
            fig = px.bar(counts, color_discrete_sequence=["#378ADD"])
            #st.plotly_chart(fig, width='stretch')

        # PIE
        elif chart == "pie":
            counts = data[col].value_counts().head(5).reset_index()
            counts.columns = [col, "count"]
            fig = px.pie(
                counts,
                names=col,
                values="count",
                color_discrete_sequence=[
                    "#7F77DD", "#1D9E75", "#D85A30",
                    "#378ADD", "#D4537E", "#BA7517"
                ]
            )
            #st.plotly_chart(fig, width='stretch')
        # elif chart == "TimeLine":
        #     fig = px.line(data, x=col, y=num_col, color_discrete_sequence=["#7F77DD"])
        #     st.plotly_chart(fig, width='stretch')
        elif chart == "TimeLine":

            df = data.copy()

            # 1. Convertir a datetime
            #df[col] = pd.to_datetime(df[col], errors="coerce", format="%Y-%m-%d")

            # 2. Eliminar filas sin fecha válida
            #df = df.dropna(subset=[col, num_col])

            # 3. Ordenar por fecha
            df = df.sort_values(col)

            # 4. Agrupar por semana (o "M" para mensual)
            df_grouped = df.groupby(pd.Grouper(key=col, freq="D")).agg({num_col: "sum"}).reset_index()
            # 5. Rolling mean (suavizado)
            #df_grouped["rolling"] = df_grouped[num_col].rolling(4).mean()

            # 6. Dibujar
            fig = px.line(
                df_grouped,
                x=col,
                y=num_col,
                labels={num_col: num_col},
                color_discrete_sequence=["#7F77DD", "#1D9E75"]
            )

            fig.update_layout(
                xaxis_title="Fecha",
                yaxis_title=num_col,
                legend_title="Series",
                hovermode="x unified"
            )
            
            #st.plotly_chart(fig, width='stretch')
            # Aplicar plantilla de Plotly según el modo seleccionado
        figures.append(fig)
    return figures
# ============================================================
# CORRELACIONES
# ============================================================
def gen_Corr(data, cols):

    if len(cols) < 2:
        st.warning("Selecciona al menos 2 columnas")
        return None

    # Scatter
    if len(cols) == 2:
        fig = px.scatter(data, x=cols[0], y=cols[1])
        st.plotly_chart(fig, width='stretch')
        return fig

    # Heatmap
    fig = px.imshow(
        data,
        color_continuous_scale=[
            "#0b0f2b", "#3b0f70", "#8c2981",
            "#de4968", "#fe9f6d", "#fcfdbf"
        ],
        template="plotly_dark"
    )
    st.plotly_chart(fig, width='stretch')
    return fig
