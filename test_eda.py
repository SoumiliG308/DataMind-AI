import pandas as pd

from modules.eda import (
    get_numeric_summary,
    get_categorical_summary,
    get_correlation_matrix
)

df = pd.read_csv("sample_data/titanic.csv")

print("\nNUMERICAL SUMMARY")
print(get_numeric_summary(df))

print("\nCATEGORICAL SUMMARY")
print(get_categorical_summary(df))

print("\nCORRELATION MATRIX")
print(get_correlation_matrix(df))
