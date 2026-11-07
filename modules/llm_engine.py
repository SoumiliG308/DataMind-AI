import streamlit as st
from openrouter import OpenRouter
import json
from modules.analytics_tools import execute_tool_call

def ask_model(prompt, model="openrouter/free"):
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]

        with OpenRouter(api_key=api_key) as client:
            response = client.responses.send(
                model=model,
                input=prompt
            )

            if response.status != "completed":
                error = (
                    response.error.message
                    if response.error
                    else f"Response ended with status: {response.status}"
                )
                return f"API Error: {error}"

            message = next(
                item for item in response.output
                if item.type == "message"
            )

            return next(
                part.text for part in message.content
                if part.type == "output_text"
            )

    except Exception as error:
        return f"OpenRouter Error: {error}"


COLUMN_SUMMARY_TOOL = {
    "type": "function",
    "function": {
        "name": "get_column_summary",
        "description": (
            "Get statistical information about a column "
            "in the uploaded dataset."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "The exact column name to analyse."
                }
            },
            "required": ["column"],
            "additionalProperties": False
        }
    }
}


GROUPED_ANALYSIS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_grouped_analysis",
        "description": (
            "Group dataset records by a categorical or numeric column "
            "and calculate an aggregation on another column. "
            "Use this for questions comparing averages, sums, counts, "
            "medians, minimums or maximums across groups."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "group_column": {
                    "type": "string",
                    "description": "Column used to create groups."
                },
                "target_column": {
                    "type": "string",
                    "description": "Column on which the calculation is performed."
                },
                "operation": {
                    "type": "string",
                    "enum": [
                        "mean",
                        "sum",
                        "count",
                        "median",
                        "min",
                        "max"
                    ],
                    "description": "Aggregation operation to perform."
                }
            },
            "required": [
                "group_column",
                "target_column",
                "operation"
            ],
            "additionalProperties": False
        }
    }
}


FILTERED_ANALYSIS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_filtered_analysis",
        "description": (
            "Filter dataset rows using a condition and perform "
            "an aggregation on the matching rows. Use this for "
            "questions involving conditions such as greater than, "
            "less than, equal to, or containing a value."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "filter_column": {
                    "type": "string",
                    "description": "Column on which the condition is applied."
                },
                "operator": {
                    "type": "string",
                    "enum": ["eq", "ne", "gt", "gte", "lt", "lte", "contains"]
                },
                "filter_value": {
                    "type": ["string", "number"],
                    "description": "Value used in the filter condition."
                },
                "target_column": {
                    "type": "string",
                    "description": "Column to analyse after filtering."
                },
                "operation": {
                    "type": "string",
                    "enum": [
                        "mean", "sum", "count",
                        "median", "min", "max", "percentage"
                    ]
                }
            },
            "required": [
                "filter_column",
                "operator",
                "filter_value",
                "target_column",
                "operation"
            ],
            "additionalProperties": False
        }
    }
}


CORRELATION_TOOL = {
    "type": "function",
    "function": {
        "name": "get_correlation_analysis",
        "description": (
            "Calculate the Pearson correlation coefficient "
            "between two numeric dataset columns. Use this when "
            "the user asks about relationships or correlations "
            "between two numerical variables."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "column1": {
                    "type": "string",
                    "description": "First numeric column."
                },
                "column2": {
                    "type": "string",
                    "description": "Second numeric column."
                }
            },
            "required": ["column1", "column2"],
            "additionalProperties": False
        }
    }
}


CHART_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_chart",
        "description": (
            "Create a visualisation specification for the uploaded dataset. "
            "Use histogram for distributions, bar for grouped comparisons, "
            "scatter for relationships between two numeric variables, "
            "and box for numeric distributions and outlier inspection."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": ["histogram", "bar", "scatter", "box"]
                },
                "x_column": {
                    "type": "string",
                    "description": "Column for the x-axis or grouping."
                },
                "y_column": {
                    "type": ["string", "null"],
                    "description": "Numeric y-axis column, if required."
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["mean", "sum", "median", "count"],
                    "description": "Aggregation for bar charts."
                }
            },
            "required": [
                "chart_type",
                "x_column",
                "y_column",
                "aggregation"
            ],
            "additionalProperties": False
        }
    }
}


def request_tool_call(prompt, model="openrouter/free"):
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]

        with OpenRouter(api_key=api_key) as client:
            response = client.chat.send(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are DataMind AI, an intelligent data analyst. "
                            "Use the available tool whenever the user asks "
                            "for statistics about a specific dataset column."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                tools=[COLUMN_SUMMARY_TOOL],
                tool_choice="auto",
                stream=False
            )

            message = response.choices[0].message

            return {
                "content": message.content,
                "tool_calls": message.tool_calls
            }

    except Exception as error:
        return {
            "content": f"OpenRouter Error: {error}",
            "tool_calls": None
        }

def run_data_analyst(df, prompt, model="openrouter/free"):
    """Run a dataset-aware AI analysis with controlled tool execution."""

    messages = [
        
        {
        "role": "system",
        "content": (
            "You are DataMind AI, a professional data analyst.\n\n"
            f"AVAILABLE DATASET COLUMNS: {df.columns.tolist()}\n\n"
            
            "IMPORTANT RULES:\n"
            "1. Use only exact column names from the dataset.\n"
            "2. For a single column's statistics, use get_column_summary.\n"
            "3. For comparisons across groups, use get_grouped_analysis.\n"
            "4. For conditions or filtered calculations, use get_filtered_analysis.\n"
            "5. For relationships between two numeric columns, use get_correlation_analysis.\n"
            "6. Do not call multiple tools for a question that needs only one tool.\n"
            "7. After receiving tool results, explain them directly. Do not repeat a completed calculation.\n"
            "8. Never invent numerical results.\n"
            "9. Correlation does not establish causation.\n"
            "10. If the user asks for a chart or plot, use generate_chart.\n"
            "11. Choose a chart type appropriate to the requested analysis.\n")
        },

        {
            "role": "user",
            "content": prompt
        }
    ]
    chart_keywords = [
    "plot", "chart", "visualise", "visualize",
    "graph", "scatter", "histogram"
    ]

    is_chart_request = any(
        keyword in prompt.lower()
        for keyword in chart_keywords
    )
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]

        with OpenRouter(api_key=api_key) as client:

            # Allow up to 3 rounds of tool requests.
            debug_log=[]
            for _ in range(5):

                response = client.chat.send(
                    model=model,
                    messages=messages,
                    tools=[COLUMN_SUMMARY_TOOL, GROUPED_ANALYSIS_TOOL, FILTERED_ANALYSIS_TOOL,
                           CORRELATION_TOOL, CHART_TOOL],
                    tool_choice=({
                            "type": "function",
                            "function": {"name": "generate_chart"}
                        }
                        if is_chart_request
                        else "auto"
                    ),
                    stream=False
                )

                message = response.choices[0].message
                tool_calls = message.tool_calls

                # If the model has finished answering, return its response.
                if not tool_calls:
                    return {"answer": message.content or "The model returned an empty response.",
                    "debug": debug_log}

                # Preserve the assistant's tool request in conversation history.
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments
                            }
                        }
                        for call in tool_calls
                    ]
                })

                # Execute each approved tool and send its result back.
                for call in tool_calls:

                    result = execute_tool_call(
                        df,
                        call.function.name,
                        call.function.arguments
                    )
                    debug_log.append({
                    "tool": call.function.name,
                    "arguments": call.function.arguments,
                    "result": result
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, default=str)
                    })

            return {
                "answer": "Analysis stopped after reaching the tool-call limit.",
                "debug": debug_log
            }
    except Exception as error:
        return f"DataMind AI Error: {error}"

def generate_followups(question, answer, model="openrouter/free"):
    """Generate relevant follow-up questions from the latest analysis."""

    prompt = f"""
You are helping a user explore a dataset through DataMind AI.

Original question:
{question}

Analysis result:
{answer}

Generate exactly 3 short, useful follow-up questions.

Rules:
1. Questions must relate to the current analysis.
2. Suggest deeper analysis, comparisons or visualisations.
3. Do not repeat the original question.
4. Do not assume columns that are not mentioned in the analysis.
5. Return ONLY a valid JSON array of 3 strings.

Example:
[
    "Can you visualise this relationship?",
    "How does this vary across passenger classes?",
    "Are there any unusual patterns?"
]
"""

    response = ask_model(prompt, model=model)

    try:
        # Extract the JSON array from the response.
        start = response.find("[")
        end = response.rfind("]")

        if start == -1 or end == -1:
            return []

        suggestions = json.loads(response[start:end + 1])

        if not isinstance(suggestions, list):
            return []

        return [
            item.strip()
            for item in suggestions
            if isinstance(item, str) and item.strip()
        ][:3]

    except (json.JSONDecodeError, AttributeError, TypeError):
        return []
