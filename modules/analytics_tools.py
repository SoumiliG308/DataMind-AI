import json
import pandas as pd


def get_column_summary(df, column):
    """
    Analyse a selected dataset column and return
    its statistical summary.
    """

    if column not in df.columns:
        return {
            "error": f"Column '{column}' does not exist."
        }

    series = df[column]

    result = {
        "column": column,
        "data_type": str(series.dtype),
        "total_records": len(series),
        "missing_values": int(series.isnull().sum()),
        "unique_values": int(series.nunique())
    }

    if pd.api.types.is_numeric_dtype(series):

        result.update({
            "mean": round(float(series.mean()), 2) if series.notna().any() else None,
            "median": round(float(series.median()), 2) if series.notna().any() else None,
            "minimum": float(series.min()) if series.notna().any() else None,
            "maximum": float(series.max()) if series.notna().any() else None
        })

    else:
        mode = series.mode()

        result["most_frequent"] = (
            str(mode.iloc[0]) if not mode.empty else None
        )

    return result


def execute_tool_call(df, tool_name, arguments):
    """Execute an approved analytical tool."""

    if tool_name != "get_column_summary":
        return {"error": "Unknown or unsupported tool."}

    try:
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        column = arguments.get("column")

        if not isinstance(column, str) or not column.strip():
            return {"error": "A valid column name is required."}

        return get_column_summary(df, column)

    except (json.JSONDecodeError, TypeError, AttributeError):
        return {"error": "Invalid tool arguments."}
