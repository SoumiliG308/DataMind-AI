import pandas as pd
import numpy as np

def get_numeric_summary(df):
    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.empty:
        return None

    summary = numeric_df.describe().T
    summary["median"] = numeric_df.median()
    summary["missing_values"] = numeric_df.isnull().sum()

    return summary.round(2)


def get_categorical_summary(df):
    categorical_df = df.select_dtypes(
        include=["object", "category", "bool"]
    )

    if categorical_df.empty:
        return None

    summary = pd.DataFrame({
        "Unique Values": categorical_df.nunique(),
        "Most Frequent": categorical_df.mode().iloc[0],
        "Missing Values": categorical_df.isnull().sum()
    })

    return summary


def get_correlation_matrix(df):
    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] < 2:
        return None

    return numeric_df.corr().round(2)
