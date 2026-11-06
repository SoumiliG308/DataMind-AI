import pandas as pd
def get_dataset_overview(df):
    overview = {
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Duplicate Rows": int(df.duplicated().sum()),
        "Memory Usage (KB)": round(df.memory_usage(deep=True).sum() / 1024,2)
    }
    return overview

def get_missing_values(df):
    missing_count = df.isnull().sum()
    missing_percentage = (df.isnull().mean() * 100).round(2)
    report = pd.DataFrame({
        "Missing Values": missing_count,
        "Missing Percentage (%)": missing_percentage
    })
    return report

def get_col_info(df):
    report = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Non-Null Count": df.notnull().sum().values,
        "Unique Values": df.nunique().values
    })
    return report