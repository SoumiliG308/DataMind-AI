import streamlit as st
from openrouter import OpenRouter
import json
from modules.analytics_tools import execute_tool_call

def get_friendly_error(error):
    error_text = str(error).lower()

    if "429" in error_text or "rate limit" in error_text:
        return (
            "Our AI service is experiencing high demand. "
            "Please try again later."
        )

    if "quota" in error_text or "credits" in error_text:
        return (
            "The AI usage limit has been reached. "
            "Please try again after the quota resets."
        )

    if "401" in error_text or "403" in error_text:
        return (
            "The AI service could not authorize this request. "
            "Please contact the administrator."
        )

    if "timeout" in error_text or "connection" in error_text:
        return (
            "We're temporarily unable to connect to the AI service. "
            "Please try again shortly."
        )

    return (
        "Something went wrong while analysing your data. "
        "Please try again later."
    )

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

def run_data_analyst(df, prompt, model="openrouter/free", history=None):
    """Run dataset-aware analysis while retaining recent conversation context."""

    system_message = {
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
            "6. Use only the approved analytical tools; never write or execute arbitrary Python code.\n"
            "7. After receiving tool results, explain them directly. Never invent numerical results.\n"
            "8. Correlation does not establish causation.\n"
            "9. If the user asks for a chart or plot, use generate_chart.\n"
            "10. Use earlier messages to resolve references such as 'that column', "
            "'the same group', or 'show it as a chart'.\n"
            "11. If a question cannot be answered from the dataset or tools, say so clearly."
        )
    }

    # Only pass ordinary conversational turns. Tool-call messages from older
    # requests are intentionally not replayed; their final answers provide context.
    recent_history = []
    for item in (history or [])[-10:]:
        if (
            isinstance(item, dict)
            and item.get("role") in ("user", "assistant")
            and isinstance(item.get("content"), str)
            and item["content"].strip()
        ):
            recent_history.append({
                "role": item["role"],
                "content": item["content"][:4000]
            })

    messages = [system_message] + recent_history + [
        {"role": "user", "content": prompt}
    ]

    chart_keywords = [
        "plot", "chart", "visualise", "visualize", "graph",
        "scatter", "histogram", "box plot", "bar chart"
    ]
    is_chart_request = any(
        keyword in prompt.lower() for keyword in chart_keywords
    )

    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]

        with OpenRouter(api_key=api_key) as client:
            debug_log = []

            # A chart request should create one chart, then move on to a
            # normal model response. Re-forcing generate_chart on every round
            # caused repeated identical charts and exhausted the tool loop.
            for round_index in range(5):
                available_tools = [
                    COLUMN_SUMMARY_TOOL,
                    GROUPED_ANALYSIS_TOOL,
                    FILTERED_ANALYSIS_TOOL,
                    CORRELATION_TOOL
                ]

                # Permit chart generation only in the first round. Once the
                # chart result is returned, the model must explain that result
                # rather than generating the same chart again.
                if not (is_chart_request and round_index > 0):
                    available_tools.append(CHART_TOOL)

                response = client.chat.send(
                    model=model,
                    messages=messages,
                    tools=available_tools,
                    tool_choice=(
                        {
                            "type": "function",
                            "function": {"name": "generate_chart"}
                        }
                        if is_chart_request and round_index == 0 else "auto"
                    ),
                    stream=False
                )

                message = response.choices[0].message
                tool_calls = message.tool_calls

                if not tool_calls:
                    answer = message.content or ""

                    if not answer.strip():
                        answer = (
                            "We couldn't complete your analysis this time. "
                            "Your data is safe. Please try again in a moment."
                        )

                    return {
                        "answer": answer,
                        "debug": debug_log,
                        "error": not bool(message.content and message.content.strip())
                    }
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
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

            # If the provider keeps requesting tools, preserve any useful
            # calculations already completed instead of returning a dead end.
            completed_tools = [
                item.get("tool", "analysis")
                for item in debug_log
            ]
            if is_chart_request and any(
                item.get("tool") == "generate_chart" for item in debug_log
            ):
                fallback_answer = (
                    "I've generated the requested chart. The model could not "
                    "finish its written interpretation within the tool-call "
                    "limit, but you can still inspect the visualisation below."
                )
            elif debug_log:
                fallback_answer = (
                    "I completed part of the analysis, but the model did not "
                    "finish its explanation. Completed tools: "
                    + ", ".join(completed_tools)
                    + ". Please try a narrower follow-up."
                )
            else:
                fallback_answer = (
                    "I couldn't complete the analysis within the tool-call "
                    "limit. Please try a more specific question."
                )

            return {
                "answer": fallback_answer,
                "debug": debug_log
            }

    except Exception as error:
        return {
            "answer": get_friendly_error(error),
            "debug": [],
            "error": True
        }

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
