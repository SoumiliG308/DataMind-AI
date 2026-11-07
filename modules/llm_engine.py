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
                "You are DataMind AI, a professional data analyst. "
                "Use the available tools to obtain actual dataset statistics. "
                "Never invent numerical results. Explain findings clearly "
                "and mention relevant limitations."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]

        with OpenRouter(api_key=api_key) as client:

            # Allow up to 3 rounds of tool requests.
            for _ in range(3):

                response = client.chat.send(
                    model=model,
                    messages=messages,
                    tools=[COLUMN_SUMMARY_TOOL],
                    tool_choice="auto",
                    stream=False
                )

                message = response.choices[0].message
                tool_calls = message.tool_calls

                # If the model has finished answering, return its response.
                if not tool_calls:
                    return message.content or "The model returned an empty response."

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

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, default=str)
                    })

            return "Analysis stopped after reaching the tool-call limit."

    except Exception as error:
        return f"DataMind AI Error: {error}"
