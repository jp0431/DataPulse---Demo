from preprocessing import feature_score
from utilities import pd    

# def gen_scores(data):
#     num_cols = data.select_dtypes(include="number").columns
#     cat_cols = data.select_dtypes(exclude="number").columns

#     num_scores = {
#                         col: feature_score(data[col])
#                         for col in num_cols
#                     }
#     cat_scores = {
#                         col: feature_score(data[col])
#                         for col in cat_cols
#                     }
#     top_num = sorted(
#                         num_scores,
#                         key=num_scores.get,
#                         reverse=True
#                     )[:5]

#     top_cat = sorted(
#                         cat_scores,
#                         key=cat_scores.get,
#                         reverse=True
#                     )[:5]
#     return top_num, top_cat

def gen_scores(data):

    # Columnas numéricas reales
    numeric_cols = [
        col for col in data.columns
        if pd.api.types.is_numeric_dtype(data[col])
    ]

    # Columnas categóricas reales
    categorical_cols = [
        col for col in data.columns
        if not pd.api.types.is_numeric_dtype(data[col])
    ]

    num_scores = {col: feature_score(data[col]) for col in numeric_cols}
    cat_scores = {col: feature_score(data[col]) for col in categorical_cols}

    top_num = sorted(num_scores, key=num_scores.get, reverse=True)
    top_cat = sorted(cat_scores, key=cat_scores.get, reverse=True)

    return top_num, top_cat
