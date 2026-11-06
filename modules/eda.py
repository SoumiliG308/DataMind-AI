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


def get_outlier_summary(df):
    """
    Detect outliers in numerical columns using the IQR method.
    """

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.empty:
        return None

    results = []

    for column in numeric_df.columns:

        # Remove missing values before calculating quartiles
        values = numeric_df[column].dropna()

        if values.empty:
            continue

        # Calculate first and third quartiles
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)

        # Calculate Interquartile Range
        IQR = Q3 - Q1

        # Calculate outlier boundaries
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Identify outliers
        outliers = values[
            (values < lower_bound) |
            (values > upper_bound)
        ]

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
