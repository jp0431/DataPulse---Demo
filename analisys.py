from utilities import pd
#Analysis
def detect_date_cols(data, min_success_ratio=0.8):
    date_cols = []

    for col in data.columns:
        s = data[col]

        # 1) Si ya es datetime, la marcamos
        if pd.api.types.is_datetime64_any_dtype(s):
            data[col] = data[col].dt.strftime("%Y-%m-%d")
            date_cols.append(col)
            continue

        # 2) Solo intentamos parsear columnas tipo object
        if s.dtype == "object":
            parsed = pd.to_datetime(s, errors="coerce", dayfirst=True)
            success_ratio = parsed.notna().mean()

            if success_ratio >= min_success_ratio:
                data[col] = parsed
                date_cols.append(col)
        if s.dtype == "int64":
            # Los timestamps en ns suelen ser > 1e17
            if s.dropna().abs().mean() > 1e17:
                data[col] = pd.to_datetime(s, unit="ns", errors="coerce")
                date_cols.append(col)

    return data,list(dict.fromkeys(date_cols))

def basic_analisis(data):
    # Detectar fechas de forma robusta
    data, date_cols = detect_date_cols(data)
    cols_num = data.select_dtypes(include="number")
    cols_cat = data.select_dtypes(exclude=["number", "datetime"])


    if len(cols_num.columns) == 0:
        estadisticas_num = "No hay columnas numéricas"
    else:
        estadisticas_num = data[cols_num.columns].describe()
    
    if len(cols_cat.columns) == 0:
        estadisticas_cat = "No hay columnas categóricas"
    else:
        estadisticas_cat = data[cols_cat.columns].describe()
    nuls = data.isnull()
    analisis = {
        "Filas": data.shape[0],
        "Columnas":  data.shape[1],
        "Filas duplicadas:": data.duplicated().sum(),
        "Número Columnas numericas": len(cols_num.columns),
        "Número Columnas categoricas": len(cols_cat.columns),
        "Número Columnas fecha": len(date_cols),
        "Columnas numericas": cols_num.columns,
        "Columnas Categoricas": cols_cat.columns,
        "Columnas fecha": date_cols,
        "Porcentaje nulos": nuls.mean().mean()*100,
        "Estadisticas numericas": estadisticas_num,
        "Estadisticas categoricas": estadisticas_cat,
        "Correlación": data[cols_num.columns].corr()
    }
    return analisis
