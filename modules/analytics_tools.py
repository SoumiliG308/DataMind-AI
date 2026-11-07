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

    try:
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        if not isinstance(arguments, dict):
            return {"error": "Invalid tool arguments."}

        if tool_name == "get_column_summary":

            column = arguments.get("column")

            if not isinstance(column, str) or not column.strip():
                return {"error": "A valid column name is required."}

            return get_column_summary(df, column)

        elif tool_name == "get_grouped_analysis":

            group_column = arguments.get("group_column")
            target_column = arguments.get("target_column")
            operation = arguments.get("operation")

            if not all(
                isinstance(value, str) and value.strip()
                for value in [group_column, target_column, operation]
            ):
                return {"error": "Invalid grouping arguments."}

            return get_grouped_analysis(
                df,
                group_column,
                target_column,
                operation
            )

        
        elif tool_name == "get_filtered_analysis":

            return get_filtered_analysis(
                df,
                arguments.get("filter_column"),
                arguments.get("operator"),
                arguments.get("filter_value"),
                arguments.get("target_column"),
                arguments.get("operation")
            )

        elif tool_name == "get_correlation_analysis":

            return get_correlation_analysis(
                df,
                arguments.get("column1"),
                arguments.get("column2")
            )

        
        elif tool_name == "generate_chart":

            return generate_chart_spec(
                df,
                arguments.get("chart_type"),
                arguments.get("x_column"),
                arguments.get("y_column"),
                arguments.get("aggregation", "mean")
            )

        else:
            return {"error": "Unknown or unsupported tool."}

    except (json.JSONDecodeError, TypeError, AttributeError):
        return {"error": "Invalid tool arguments."}

def get_grouped_analysis(df, group_column, target_column, operation):
    """
    Group dataset records and perform an aggregation.
    """

    if group_column not in df.columns:
        return {"error": f"Group column '{group_column}' does not exist."}

    if target_column not in df.columns:
        return {"error": f"Target column '{target_column}' does not exist."}

    allowed_operations = ["mean", "sum", "count", "median", "min", "max"]

    if operation not in allowed_operations:
        return {"error": "Unsupported aggregation operation."}

    try:
        grouped = df.groupby(group_column)[target_column]

        if operation == "mean":
            result = grouped.mean()
        elif operation == "sum":
            result = grouped.sum()
        elif operation == "count":
            result = grouped.count()
        elif operation == "median":
            result = grouped.median()
        elif operation == "min":
            result = grouped.min()
        else:
            result = grouped.max()

        return {
            "group_column": group_column,
            "target_column": target_column,
            "operation": operation,
            "results": result.round(2).to_dict()
        }

    except Exception as error:
        return {"error": str(error)}


def get_filtered_analysis(
    df,
    filter_column,
    operator,
    filter_value,
    target_column,
    operation
):
    """Filter dataset rows and calculate an aggregation on the result."""

    if filter_column not in df.columns:
        return {"error": f"Filter column '{filter_column}' does not exist."}

    if target_column not in df.columns:
        return {"error": f"Target column '{target_column}' does not exist."}

    try:
        series = df[filter_column]

        if operator == "eq":
            mask = series.astype(str).str.lower() == str(filter_value).lower()
        elif operator == "ne":
            mask = series.astype(str).str.lower() != str(filter_value).lower()
        elif operator == "gt":
            mask = series > float(filter_value)
        elif operator == "gte":
            mask = series >= float(filter_value)
        elif operator == "lt":
            mask = series < float(filter_value)
        elif operator == "lte":
            mask = series <= float(filter_value)
        elif operator == "contains":
            mask = series.astype(str).str.contains(
                str(filter_value), case=False, na=False
            )
        else:
            return {"error": "Unsupported filter operator."}

        filtered_df = df.loc[mask].copy()

        if filtered_df.empty:
            return {"error": "No rows matched the given filter."}

        values = filtered_df[target_column]

        if operation == "count":
            result = int(values.count())
        elif operation == "mean":
            result = float(values.mean())
        elif operation == "sum":
            result = float(values.sum())
        elif operation == "median":
            result = float(values.median())
        elif operation == "min":
            result = float(values.min())
        elif operation == "max":
            result = float(values.max())
        elif operation == "percentage":
            numeric_values = pd.to_numeric(values, errors="coerce").dropna()

            if not set(numeric_values.unique()).issubset({0, 1}):
                return {
                    "error": "Percentage aggregation requires a binary 0/1 target column."
                }

            result = float(numeric_values.mean() * 100)
        else:
            return {"error": "Unsupported aggregation operation."}

        return {
            "filter": {
                "column": filter_column,
                "operator": operator,
                "value": filter_value
            },
            "target_column": target_column,
            "operation": operation,
            "matching_rows": int(len(filtered_df)),
            "total_rows": int(len(df)),
            "result": round(result, 2)
        }

    except (TypeError, ValueError):
        return {"error": "The filter value is incompatible with the selected column."}
    except Exception as error:
        return {"error": str(error)}


def get_correlation_analysis(df, column1, column2):
    """Calculate correlation between two numeric columns."""

    if column1 not in df.columns or column2 not in df.columns:
        return {"error": "One or both columns do not exist."}

    if column1 == column2:
        return {"error": "Please select two different columns."}

    try:
        if not pd.api.types.is_numeric_dtype(df[column1]):
            return {"error": f"{column1} must be numeric."}

        if not pd.api.types.is_numeric_dtype(df[column2]):
            return {"error": f"{column2} must be numeric."}

        valid_data = df[[column1, column2]].dropna()

        if len(valid_data) < 2:
            return {"error": "Not enough valid records to calculate correlation."}

        correlation = valid_data[column1].corr(valid_data[column2])

        return {
            "column1": column1,
            "column2": column2,
            "correlation": round(float(correlation), 4),
            "valid_records": len(valid_data)
        }

    except Exception as error:
        return {"error": str(error)}


def generate_chart_spec(
    df,
    chart_type,
    x_column,
    y_column=None,
    aggregation="mean"
):
    """Validate a chart request and return a safe Plotly chart specification."""

    if x_column not in df.columns:
        return {"error": f"Column '{x_column}' does not exist."}

    if y_column and y_column not in df.columns:
        return {"error": f"Column '{y_column}' does not exist."}

    if chart_type not in ["histogram", "bar", "scatter", "box"]:
        return {"error": "Unsupported chart type."}

    if chart_type in ["histogram", "scatter", "box"]:
        numeric_column = y_column if chart_type == "box" else x_column

        if not pd.api.types.is_numeric_dtype(df[numeric_column]):
            return {"error": f"Column '{numeric_column}' must be numeric."}

    if chart_type == "scatter":
        if not y_column:
            return {"error": "Scatter plots require both x and y columns."}

        if not pd.api.types.is_numeric_dtype(df[y_column]):
            return {"error": f"Column '{y_column}' must be numeric."}

    if chart_type in ["bar", "box"] and not y_column:
        return {"error": f"{chart_type.title()} charts require a y column."}

    if chart_type == "bar":
        if aggregation not in ["mean", "sum", "median", "count"]:
            return {"error": "Unsupported bar chart aggregation."}

        if aggregation != "count" and not pd.api.types.is_numeric_dtype(df[y_column]):
            return {"error": f"Column '{y_column}' must be numeric for this aggregation."}

    return {
        "chart_type": chart_type,
        "x_column": x_column,
        "y_column": y_column,
        "aggregation": aggregation,
        "title": f"{chart_type.title()} chart: {x_column}"
    }
