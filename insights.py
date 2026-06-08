from utilities import pd
def severity_from_value(value, thresholds=(0.8, 0.5)):
    if value >= thresholds[0]:
        return "🔴 CRITICO"
    elif value >= thresholds[1]:
        return "🟡 IMPORTANTE"
    else:
        return "🟢 INFO"
    
def analyze_numeric(series):
    insights = []
    name = series.name

    # Conversión segura
    s = pd.to_numeric(series, errors="coerce").dropna()

    if len(s) == 0:
        return []   # nunca None

    # Skew
    skew = s.skew()
    if abs(skew) > 1:
        sev = severity_from_value(abs(skew), (2, 1))
        insights.append((sev, f"{name} presenta alta asimetría (skew={skew:.2f})"))

    # Outliers
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    outlier_ratio = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).mean()

    if outlier_ratio > 0.05:
        sev = severity_from_value(outlier_ratio, (0.2, 0.1))
        insights.append((sev, f"{name} contiene {outlier_ratio:.1%} de outliers"))

    return insights


def analyze_categorical(series):
    insights = []
    name = series.name

    vc = series.value_counts(normalize=True, dropna=True)

    if len(vc) == 0:
        return insights

    dominance = vc.iloc[0]

    # Dominancia
    if dominance > 0.8:
        sev = severity_from_value(dominance, (0.9, 0.8))
        insights.append((sev, f"{name} está dominada por una categoría ({dominance:.1%})"))

    # Pocas categorías
    if len(vc) <= 3:
        insights.append(("🟡 IMPORTANTE", f"{name} tiene pocas categorías ({len(vc)})"))

    return insights
def analyze_correlations(corr):
    insights = []

    for i, col1 in enumerate(corr.columns):
        for j, col2 in enumerate(corr.columns):
            if j <= i:
                continue

            value = corr.loc[col1, col2]

            if abs(value) > 0.7:
                insights.append(("🔴 CRITICO",
                                 f"Multicolinealidad fuerte entre {col1} y {col2} ({value:.2f})"))
            elif abs(value) > 0.5:
                insights.append(("🟡 IMPORTANTE",
                                 f"Correlación relevante entre {col1} y {col2} ({value:.2f})"))

    return insights
    
def gen_insights(data, analisis, imputation_log, target=None):
    critical, important, info = [], [], []

    # Información general
    info.append(f"Dataset con {analisis['Filas']} filas y {analisis['Columnas']} columnas.")
    info.append(f"{analisis['Número Columnas numericas']} numéricas, "
                f"{analisis['Número Columnas categoricas']} categóricas.")
    info.append(f"Se detectaron {analisis['Porcentaje nulos']:.2f}% de valores nulos.")

    # Numéricas
    for col in analisis["Columnas numericas"]:
        for sev, msg in analyze_numeric(data[col]):
            if sev == "🔴 CRITICO": critical.append(msg)
            elif sev == "🟡 IMPORTANTE": important.append(msg)
            else: info.append(msg)

    # Categóricas
    for col in analisis["Columnas Categoricas"]:
        for sev, msg in analyze_categorical(data[col]):
            if sev == "🔴 CRITICO": critical.append(msg)
            elif sev == "🟡 IMPORTANTE": important.append(msg)
            else: info.append(msg)

    # Correlaciones
    for sev, msg in analyze_correlations(analisis["Correlación"]):
        if sev == "🔴 CRITICO": critical.append(msg)
        else: important.append(msg)

    # Target (si existe)
    if target is not None:
        num_cols = data.select_dtypes(include="number")
        for col in num_cols.columns:
            if col == target:
                continue
            corr_val = data[[col, target]].corr().iloc[0, 1]
            if abs(corr_val) > 0.3:
                info.append(f"🎯 {col} parece influir en {target} (corr={corr_val:.2f})")

    # Log de imputación
    info.extend(imputation_log)

    return {
        "🔴 Critica": critical,
        "🟡 Importante": important,
        "🟢 Info": info
    }


def extract_signals(data):
    signals = {
        "high_missing": (data.isnull().mean() > 0.3).sum(),
        "skewed_vars": 0,
        "high_outliers": 0
    }

    num = data.select_dtypes(include="number")

    for col in num.columns:
        s = num[col].dropna()
        if len(s) == 0:
            continue

        if abs(s.skew()) > 1:
            signals["skewed_vars"] += 1

        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        out = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).mean()

        if out > 0.05:
            signals["high_outliers"] += 1

    return signals
def generate_summary(data, critical, important, signals):
    summary = []

    summary.append(f"El dataset contiene {data.shape[0]} registros y {data.shape[1]} variables.")

    if signals["high_missing"] > 0:
        summary.append(f"{signals['high_missing']} variables presentan altos valores faltantes.")

    if signals["skewed_vars"] > 0:
        summary.append(f"{signals['skewed_vars']} variables presentan distribuciones sesgadas.")

    if signals["high_outliers"] > 0:
        summary.append(f"{signals['high_outliers']} variables contienen outliers significativos.")

    if critical:
        summary.append(f"Problema principal detectado: {critical[0]}")

    summary.append("Se identifican relaciones relevantes entre variables que pueden ser útiles para modelado.")

    return " ".join(summary)


def build_report(data, insights, chart_plan, summary):
  report = {
      "summary": summary,
      "insights": insights,
      "charts": chart_plan,
      "meta": {
          "rows": len(data),
          "cols": len(data.columns)
      }
    }
  return report

def dataset_score(data, analisis, signals):
    score = 100

    # Missing
    missing_ratio = data.isnull().mean()
    for ratio in missing_ratio:
        if ratio > 0.30:
            score -= 15
        elif ratio > 0.05:
            score -= 5

    # Numéricas
    num = data.select_dtypes(include="number")
    for col in num.columns:
        s = num[col].dropna()
        if len(s) == 0:
            continue

        if abs(s.skew()) > 1:
            score -= 3

        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        out = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).mean()

        if out > 0.05:
            score -= 4

    # Categóricas
    cat = data.select_dtypes(exclude="number")
    for col in cat.columns:
        vc = data[col].value_counts(normalize=True)
        if len(vc) > 0 and vc.iloc[0] > 0.8:
            score -= 3

    # Correlaciones
    corr = analisis["Correlación"]
    for i, col1 in enumerate(corr.columns):
        for j, col2 in enumerate(corr.columns):
            if j <= i:
                continue
            if abs(corr.loc[col1, col2]) > 0.5:
                score -= 2

    # Señales globales

    score -= signals.get("high_missing", 0) * 2
    score -= signals.get("high_duplicates", 0) * 2
    score -= signals.get("high_cardinality", 0) * 2
    return max(0, min(100, score))