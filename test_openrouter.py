
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.llm_engine import (
    run_data_analyst,
    generate_followups
)

st.title("DataMind AI - Conversational Data Analyst")

# Initialise session state
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "followups" not in st.session_state:
    st.session_state.followups = []

# Dataset upload
uploaded_file = st.file_uploader(
    "Upload a CSV dataset",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.astype(str).str.strip()

    st.success(
        f"Loaded {df.shape[0]} rows and {df.shape[1]} columns."
    )

    st.caption("Available columns:")
    st.write(df.columns.tolist())

    # Apply a selected follow-up before creating the text input.
    if "pending_question" in st.session_state:
        st.session_state["analyst_question"] = (
            st.session_state.pop("pending_question")
        )
    # Question input
    question = st.text_input(
        "Ask your dataset",
        key="analyst_question",
        placeholder="Calculate the Pearson correlation between age and fare."
    )

    if st.button("Analyse") and question.strip():

        with st.spinner("DataMind AI is analysing..."):
            answer = run_data_analyst(df, question)

        
        if isinstance(answer, dict):
            answer_text = answer.get("answer", "")
            debug_data = answer.get("debug", [])

        else:
            answer_text = str(answer)
            debug_data = []

            # Don't generate follow-ups for API errors.
            if answer_text.startswith(
                ("DataMind AI Error:", "OpenRouter Error:", "API Error:")
            ):
                st.error(answer_text)
                st.stop()

        # Store both types of answers in a consistent format.
        st.session_state.last_answer = {
            "answer": answer_text,
            "debug": debug_data
        }

        st.session_state.last_question = question

        with st.spinner("Generating follow-up questions..."):
            st.session_state.followups = generate_followups(
                question,
                answer_text
            )
    # Display the latest analysis
    if st.session_state.last_answer:

        answer = st.session_state.last_answer

        st.divider()

        st.subheader("DataMind AI's Answer")
        st.markdown(answer["answer"])

        st.subheader("Debug Log")
        st.json(answer["debug"])

        # Render charts requested by the AI
        for item in answer["debug"]:

            if item["tool"] == "generate_chart":

                spec = item["result"]

                if "error" in spec:
                    st.error(spec["error"])
                    continue

                chart_type = spec["chart_type"]
                x = spec["x_column"]
                y = spec["y_column"]

                st.subheader("DataMind AI Visualisation")

                if chart_type == "histogram":

                    fig = px.histogram(
                        df,
                        x=x,
                        title=f"Distribution of {x}"
                    )

                elif chart_type == "scatter":

                    fig = px.scatter(
                        df,
                        x=x,
                        y=y,
                        title=f"{y} vs {x}"
                    )

                elif chart_type == "box":

                    fig = px.box(
                        df,
                        x=x,
                        y=y,
                        title=f"Distribution of {y} by {x}"
                    )

                elif chart_type == "bar":

                    grouped = df.groupby(
                        x, dropna=False
                    )[y]

                    if spec["aggregation"] == "count":
                        chart_df = grouped.count().reset_index(
                            name="count"
                        )
                        value_column = "count"

                    else:
                        chart_df = (
                            getattr(grouped, spec["aggregation"])()
                            .reset_index(name=spec["aggregation"])
                        )
                        value_column = spec["aggregation"]

                    fig = px.bar(
                        chart_df,
                        x=x,
                        y=value_column,
                        title=f"{spec['aggregation'].title()} of {y} by {x}"
                    )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"datamind_chart_{chart_type}_{x}_{y}"
                )

        # Follow-up suggestions
        st.subheader("Explore this analysis further")

        if st.session_state.followups:

            
            for index, suggestion in enumerate(st.session_state.followups):

                if st.button(suggestion, key=f"followup_{index}"):
                    st.session_state["pending_question"] = suggestion
                    st.rerun()

        else:
            st.caption(
                "No follow-up suggestions were generated. "
                "You can ask another question above."
            )

else:
    st.info("Upload a CSV file to start analysing your dataset.")
