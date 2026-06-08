from utilities import pd
#preprocessing
def calculate_outlier_ratio(series):
    # eliminar nulos
    if len(series) == 0:
      return 0, 0
    series = series.dropna()

    # cuartiles
    series = series.astype(float)

    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)

    # rango intercuartílico
    IQR = Q3 - Q1

    # límites
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # detectar outliers
    outliers = series[
        (series < lower_bound) |
        (series > upper_bound)
    ]

    # ratio

    outlier_ratio = len(outliers) / len(series)
    skewness = series.skew()
    return outlier_ratio, skewness

def preprocessing_data(data):

    imputation_log = []
    imputation_log.append("--------- TRATAMIENTO DE NULOS -----------------")

    null_values = ["", " ", "na", "n/a", "null", "none", "NaN", "N/A", "?", "--", "nan"]

    for c in data.columns:
        if pd.api.types.is_datetime64_any_dtype(data[c]):
            imputation_log.append(f"{c}: columna fecha, omitida")
            continue
        # Normalizar nulos
        data[c] = data[c].replace(null_values, pd.NA)

        n = data[c].isnull().sum()
        percen_nul = round((n * 100) / data.shape[0], 2)

        # Conversión segura a numérico
        numeric_series = pd.to_numeric(data[c], errors="coerce")

        is_numeric_real = numeric_series.notna().sum() > 0

        # =====================================================
        # CASO 1: pocos nulos (<5%)
        # =====================================================
        if 0 < percen_nul < 5:

            if is_numeric_real:
                data[c] = numeric_series.fillna(numeric_series.median())
                imputation_log.append(f"{c}: imputado con mediana ({percen_nul}%)")
            else:
                mode = data[c].mode(dropna=True)
                data[c] = data[c].fillna(mode[0] if len(mode) else "UNKNOWN")
                imputation_log.append(f"{c}: imputado con moda ({percen_nul}%)")

        # =====================================================
        # CASO 2: nulos moderados (5–30%)
        # =====================================================
        elif 5 <= percen_nul < 30:

            if is_numeric_real:
                outlier_ratio, skewness = calculate_outlier_ratio(numeric_series)

                if outlier_ratio > 0.05 or abs(skewness) > 1:
                    data[c] = numeric_series.fillna(numeric_series.median())
                    imputation_log.append(f"{c}: mediana ({percen_nul}%, outliers={outlier_ratio:.2f})")
                else:
                    data[c] = numeric_series.fillna(numeric_series.mean())
                    imputation_log.append(f"{c}: media ({percen_nul}%)")
        
            else:
                mode = data[c].mode(dropna=True)
                data[c] = data[c].fillna(mode[0] if len(mode) else "UNKNOWN")
                imputation_log.append(f"{c}: moda ({percen_nul}%)")

        # =====================================================
        # CASO 3: muchos nulos (>30%)
        # =====================================================
        elif percen_nul >= 30:

            if is_numeric_real:
                data[c] = numeric_series.fillna(numeric_series.median())
                imputation_log.append(f"{c}: demasiados nulos, imputado con mediana ({percen_nul}%)")
            else:
                data[c] = data[c].fillna("UNKNOWN")
                imputation_log.append(f"{c}: demasiados nulos, imputado con UNKNOWN ({percen_nul}%)")
        

    return data, imputation_log



def feature_score(series):
    score = 0
    nunique = series.nunique()
    ratio = nunique / len(series)

    if pd.api.types.is_numeric_dtype(series):
        # ✅ Mismo fix aquí
        series = series.astype(float)
        score += min(ratio * 2, 2)
        outlier_ratio, skew = calculate_outlier_ratio(series)
        score += min(outlier_ratio * 3, 3)
        if abs(skew) > 1:
            score += 1

    # CATEGÓRICAS
    else:
        if nunique > 50:
            return 0
        if 2 <= nunique <= 15:
            score += 3
        vc = series.value_counts(normalize=True)
        if len(vc) > 0 and vc.iloc[0] < 0.9:
            score += 2

    # Missing
    score += series.isnull().mean()

    return score
