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



def get_outlier_summary(df, exclude_columns=None):
    if exclude_columns is None:
        exclude_columns = []

    numeric_df = df.select_dtypes(include=np.number)

    # Remove user-selected columns
    numeric_df = numeric_df.drop(
        columns=exclude_columns,
        errors="ignore"
    )

    if numeric_df.empty:
        return None

    results = []

    for column in numeric_df.columns:

        values = numeric_df[column].dropna()

        if values.empty:
            continue

        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outlier_mask = (
            (values < lower_bound) |
            (values > upper_bound)
        )

        outliers = values[outlier_mask]

        results.append({
            "Column": column,
            "Q1": round(Q1, 2),
            "Q3": round(Q3, 2),
            "IQR": round(IQR, 2),
            "Lower Bound": round(lower_bound, 2),
            "Upper Bound": round(upper_bound, 2),
            "Outlier Count": len(outliers),
            "Outlier Percentage (%)": round(
                len(outliers) / len(values) * 100, 2
            )
        })

    return pd.DataFrame(results)


def get_outlier_records(df, column):
    """
    Return rows containing outliers in the selected column
    using the 1.5 × IQR method.
    """

    values = df[column].dropna()

    if values.empty:
        return pd.DataFrame()

    Q1 = values.quantile(0.25)
    Q3 = values.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outlier_mask = (
        (df[column] < lower_bound) |
        (df[column] > upper_bound)
    )

    outlier_records = df.loc[outlier_mask].copy()

    return outlier_records

