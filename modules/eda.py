import pandas as pd
import numpy as np


# Column names that usually identify records rather than measure a feature.
_ID_EXACT_NAMES = {
    "id", "uuid", "rownumber", "row_number", "index", "serial_number",
    "customerid", "customer_id", "record_id", "transaction_id"
}
_ID_PREFIXES = (
    "customer", "account", "employee", "user", "order",
    "transaction", "row", "record", "product", "client"
)


def get_identifier_columns(df):
    """Detect likely identifier columns using names and near-unique values."""
    identifiers = []
    row_count = len(df)

    for column in df.columns:
        name = str(column).strip().lower().replace(" ", "_")
        series = df[column]
        unique_count = series.nunique(dropna=True)
        unique_ratio = unique_count / row_count if row_count else 0

        name_hint = (
            name in _ID_EXACT_NAMES
            or name.endswith("_id")
            or any(name == prefix + "id" for prefix in _ID_PREFIXES)
        )
        # Use semantic name clues for numeric IDs. Do not classify every
        # near-unique numeric measurement as an ID (e.g. Age or CreditScore).
        if name_hint:
            identifiers.append(column)

    return identifiers


def get_binary_numeric_columns(df):
    """Return numeric columns with at most two non-null distinct values."""
    result = []
    for column in df.select_dtypes(include=np.number).columns:
        values = df[column].dropna().unique()
        if len(values) <= 2:
            result.append(column)
    return result


def get_numeric_columns(df, include_identifiers=False):
    columns = df.select_dtypes(include=np.number).columns.tolist()
    if not include_identifiers:
        identifiers = get_identifier_columns(df)
        columns = [column for column in columns if column not in identifiers]
    return columns


def get_categorical_columns(df, include_identifiers=False):
    columns = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    if not include_identifiers:
        identifiers = set(get_identifier_columns(df))
        row_count = len(df)
        # Avoid ID-like/high-cardinality text fields such as names and addresses
        # in default charts. They remain available through the opt-in setting.
        columns = [
            column for column in columns
            if column not in identifiers
            and not (
                row_count >= 20
                and df[column].nunique(dropna=True) >= 20
                and df[column].nunique(dropna=True) / row_count >= 0.5
            )
        ]
    return columns


def get_numeric_summary(df, include_identifiers=False):
    columns = get_numeric_columns(df, include_identifiers=include_identifiers)
    numeric_df = df[columns]

    if numeric_df.empty:
        return None

    summary = numeric_df.describe().T
    summary["median"] = numeric_df.median()
    summary["missing_values"] = numeric_df.isnull().sum()
    return summary.round(2)


def get_categorical_summary(df, include_identifiers=False):
    columns = get_categorical_columns(df, include_identifiers=include_identifiers)
    categorical_df = df[columns]

    if categorical_df.empty:
        return None

    modes = categorical_df.mode(dropna=True)
    most_frequent = modes.iloc[0] if not modes.empty else pd.Series(index=columns, dtype=object)

    summary = pd.DataFrame({
        "Unique Values": categorical_df.nunique(),
        "Most Frequent": most_frequent,
        "Missing Values": categorical_df.isnull().sum()
    })
    return summary


def get_correlation_matrix(df, include_identifiers=False):
    columns = df.select_dtypes(include=np.number).columns.tolist()
    if not include_identifiers:
        identifiers = set(get_identifier_columns(df))
        columns = [column for column in columns if column not in identifiers]

    numeric_df = df[columns]
    if numeric_df.shape[1] < 2:
        return None
    return numeric_df.corr().round(2)


def get_default_outlier_exclusions(df):
    """IDs and binary indicator columns are excluded from IQR by default."""
    return sorted(
        set(get_identifier_columns(df)) | set(get_binary_numeric_columns(df)),
        key=lambda value: list(df.columns).index(value)
    )


def get_outlier_summary(df, exclude_columns=None):
    if exclude_columns is None:
        exclude_columns = get_default_outlier_exclusions(df)

    numeric_df = df.select_dtypes(include=np.number).drop(
        columns=exclude_columns, errors="ignore"
    )
    if numeric_df.empty:
        return None

    results = []
    for column in numeric_df.columns:
        values = numeric_df[column].dropna()
        if values.empty:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = values[(values < lower_bound) | (values > upper_bound)]

        results.append({
            "Column": column,
            "Q1": round(q1, 2),
            "Q3": round(q3, 2),
            "IQR": round(iqr, 2),
            "Lower Bound": round(lower_bound, 2),
            "Upper Bound": round(upper_bound, 2),
            "Outlier Count": int(len(outliers)),
            "Outlier Percentage (%)": round(len(outliers) / len(values) * 100, 2)
        })

    return pd.DataFrame(results)


def get_outlier_records(df, column):
    """Return rows outside the 1.5 × IQR fences for one numeric column."""
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return pd.DataFrame()

    values = df[column].dropna()
    if values.empty:
        return pd.DataFrame()

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    return df.loc[outlier_mask].copy()
