
import streamlit as st
import pandas as pd

from modules.llm_engine import run_data_analyst

st.set_page_config(page_title="DataMind AI Test")

st.title("DataMind AI - Complete Agent Test")

uploaded_file = st.file_uploader(
    "Upload a CSV dataset",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    st.write("Available columns:", df.columns.tolist())

    question = st.text_input(
        "Ask your dataset a question",
        placeholder="What is the average age?"
    )

    if st.button("Analyse Dataset") and question:
        with st.spinner("DataMind AI is analysing..."):
            answer = run_data_analyst(df, question)

        st.subheader("DataMind AI's Answer")
        st.write(answer)
