from insights import gen_insights, extract_signals, generate_summary
def gen_insights_summary(data, analisis, imputation_log):
    insights = gen_insights(data, analisis, imputation_log)
    signals = extract_signals(data)

    summary = generate_summary(
                    data,
                    insights.get("🔴 Critica"),
                    insights.get("🟡 Importante"),
                    signals
                )
    return insights,signals,summary