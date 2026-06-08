from utilities import pd, csv, st, chardet
from visualization import render_charts_for_col_html
from core.scorer import gen_scores
from core.gen_charts import gen_charts

# def load_csv_safely(file):
#     encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1", "iso-8859-1"]
#     last_error = None

#     for enc in encodings:
#         try:
#             # Detectar separador
#             sep = detect_separator(file, enc)

#             df = pd.read_csv(file, encoding=enc, sep=sep)

#             # Validación: ¿tiene columnas reales?
#             if len(df.columns) == 1 and df.columns[0] == df.iloc[:,0].name:
#                 # Puede estar mal parseado
#                 raise ValueError("Archivo mal parseado, probando siguiente encoding")

#             print(f"✔ Archivo cargado con encoding: {enc} y separador: '{sep}'")
#             return df

#         except Exception as e:
#             last_error = e
#             file.seek(0)
#             continue

#     raise ValueError(f"No se pudo leer el archivo. Último error: {last_error}")

def clean_columns(df):
    df.columns = (
        df.columns
        .str.encode("latin1", "replace")
        .str.decode("latin1")
        .str.replace("ï»¿", "", regex=False)
        .str.strip()
    )
    return df
# def load_csv_auto(file, encoding):
#     try:
#         print("Separator: ,")
#         return pd.read_csv(file, sep=",", encoding= encoding)
        
#     except:
#         print("Separator: ;")
#         return pd.read_csv(file, sep=";",  encoding= encoding)

# def detect_separator(file, encoding):
#     file.seek(0)
#     sample = file.read(2048).decode(encoding, errors="ignore")
#     file.seek(0)

#     dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|", ':'])
#     return dialect.delimiter

def exportar(analisis, summary, insights):
    report = []
    report.append("-----ANALISIS EXPLORATORIO AUTOMATICO-----")
    report.append("====================================\n\n")
    report.append("INFORMACIÓN DEL DATASET\n")
    for k, v in analisis.items():
        report.append(f"- {k}: {v}")
    report.append("\n\n")
    report.append("RESUMEN EJECUTIVO\n")
    report.append(summary + "\n\n")

    report.append("INSIGHTS\n")
    for severity, items in insights.items():
        report.append(f"{severity}\n")
        for i in items:
            report.append(f"  - {i}")
        report.append("\n")
    
    return "\n".join(report)

def exportar_html(data, report):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
    body {{
        font-family: Arial, sans-serif;
        background:#f5f7fb;
        margin:40px;
    }}
    .card {{
        background:white;
        padding:20px;
        border-radius:12px;
        margin-bottom:20px;
        box-shadow:0 2px 10px rgba(0,0,0,0.08);
    }}
    .charts-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 20px;
    }}
    .chart-card {{
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        min-width: 0;  /* evita overflow en grid */
    }}
    .chart-card h3 {{
        margin: 0 0 10px 0;
        font-size: 14px;
        color: #555;
    }}
    </style>
    </head>
    <body>
    <h1>📊 DataPulse Report</h1>
    <div class="card">
        <h2>Resumen Ejecutivo</h2>
        <p>{report["summary"]}</p>
    </div>
    """

    top_num, top_cat = gen_scores(data)
    chart_plan, charts = gen_charts(top_num, top_cat, data)

    html += "<div class='card'><h2>Insights Críticos</h2><ul>"
    for item in report["insights"]["🔴 Critica"]:
        html += f"<li>{item}</li>"
    html += "</ul></div>"

    html += "<div class='card'><h2>Insights Importantes</h2><ul>"
    for item in report["insights"]["🟡 Importante"]:
        html += f"<li>{item}</li>"
    html += "</ul></div>"

    html += "<div class='card'><h2>Información</h2><ul>"
    for item in report["insights"]["🟢 Info"]:
        html += f"<li>{item}</li>"
    html += "</ul></div>"

    # Visualizaciones en grid de 3 columnas
    html += "<h1>Visualizaciones</h1>"
    html += "<div class='charts-grid'>"

    for col, chart_types in chart_plan.items():
        figs = render_charts_for_col_html(col, chart_types, data)
        for fig in figs:
            # Ajusta el tamaño de la figura al contenedor
            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=40, b=100),
                title_text=col,
                title_font_size=13,
            )
            html += "<div class='chart-card'>"
            html += fig.to_html(full_html=False, include_plotlyjs="cdn")
            html += "</div>"

    html += "</div>"  # cierre charts-grid
    html += "</body></html>"

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)

    return html
def detect_delimiter(sample):
    """
    Detecta delimitador contando cuál aparece de forma más consistente.
    Mucho más robusto que csv.Sniffer().
    """
    candidates = [",", ";", "\t", "|", ":"]
    counts = {d: sample.count(d) for d in candidates}
    best = max(counts, key=counts.get)

    # Si el mejor delimitador aparece muy poco, no es fiable
    if counts[best] < 2:
        return None

    return best

def load_file(file):
    punto  = "."
    indices = [i for i, letra in enumerate(file.name) if letra == punto]
    extension = file.name[indices.pop():].lower()
    if extension in [".csv"]:
        return load_csv_safely(file)
    elif extension in [".xlsx"]:
        return pd.read_excel(file)  
    else:
        raise ValueError(f"Formato no soportado: {extension}")

    
def load_csv_safely(file):

    # 1. Leer bytes para detectar encoding
    raw = file.read()
    file.seek(0)

    enc = chardet.detect(raw)["encoding"] or "utf-8"

    # 2. Tomar una muestra para detectar delimitador
    sample = raw[:5000].decode(enc, errors="ignore")

    delimiter = detect_delimiter(sample)

    # 3. Si no se detecta, probar todos los delimitadores
    delimiters = [delimiter] if delimiter else [",", ";", "\t", "|", ":"]

    last_error = None

    for sep in delimiters:
        try:
            df = pd.read_csv(
                file,
                sep=sep,
                encoding=enc,
                engine="python",
                on_bad_lines="skip",
                quotechar='"',
                escapechar="\\"
            )

            # Si tiene más de 1 columna, el separador es correcto
            if df.shape[1] > 1:
                file.seek(0)
                return df

        except Exception as e:
            last_error = e
            file.seek(0)
            continue

    raise ValueError(f"No se pudo leer el archivo. Último error: {last_error}")
