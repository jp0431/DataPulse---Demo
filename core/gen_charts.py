
from visualization import generate_chart_plan


def gen_charts(top_num, top_cat, data):
    top_cols = top_num + top_cat
    data_top = data[top_cols].copy()

    chart_plan = generate_chart_plan(data_top)

    # charts y chart_plan son lo mismo ahora
    return chart_plan, chart_plan