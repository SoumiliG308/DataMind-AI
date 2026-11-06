import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="DataMind AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------
# APPLICATION HEADER
# --------------------------------

st.title("DataMind AI")

st.markdown(
    """
    ### Your Intelligent Data Analytics Assistant

    Upload datasets, discover patterns, explore insights,
    and interact with your data using natural language.
    """
)

st.divider()

# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:
    st.title("DataMind AI")

    st.markdown("### Navigation")

    page = st.radio(
        "Choose a module",
        [
            "Dashboard",
            "Data Health Audit",
            "Exploratory Data Analysis",
            "AI Data Analyst",
            "Executive Reports"
        ]
    )

    st.divider()

    st.caption("Version 1.0 | Development Build")

# --------------------------------
# DASHBOARD
# --------------------------------

if page == "Dashboard":

    st.subheader("Welcome to DataMind AI!")

    st.write(
        "Your complete workspace for intelligent data analysis."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Modules", "4")
    col2.metric("Datasets", "0")
    col3.metric("AI Engine", "Gemini")
    col4.metric("Status", "Building")

    st.divider()

    st.subheader("What can DataMind AI do?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            **1. Ingestion & Health Audit**

            - Upload CSV datasets
            - Inspect data types
            - Identify missing values
            - Detect duplicate records
            """
        )

        st.markdown(
            """
            **2. Automated Exploratory Data Analysis**

            - Statistical summaries
            - Correlation analysis
            - Outlier detection
            - Interactive visualisations
            """
        )

    with col2:
        st.markdown(
            """
            **3. Conversational AI Data Analyst**

            - Ask questions in natural language
            - Generate analytical results
            - Explore data through charts
            - Receive AI-powered explanations
            """
        )

        st.markdown(
            """
            **4. Executive Dossier Generator**

            - Summarise important findings
            - Identify trends and anomalies
            - Generate downloadable reports
            """
        )

    st.divider()

    st.info(
        "DataMind AI is under active development. "
        "The first module is coming next!"
    )

# --------------------------------
# PLACEHOLDER MODULE PAGES
# --------------------------------

elif page == "Data Health Audit":
    from modules.data_loader import load_csv
    from modules.data_quality import get_dataset_overview, get_missing_values, get_col_info

    st.header("Data Health Audit")
    st.write("Upload one or more CSV datasets to inspect there structure and data quality.")

    uploaded_files = st.file_uploader(
        "Upload CSV datasets",
        type=["csv"],
        accept_multiple_files=True
    )
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.divider()

            st.subheader(f" {uploaded_file.name}")

            df = load_csv(uploaded_file)

            if df is not None:

                # Dataset overview
                st.markdown("### Dataset Overview")

                overview = get_dataset_overview(df)

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Rows", overview["Rows"])
                col2.metric("Columns", overview["Columns"])
                col3.metric(
                    "Duplicate Rows",
                    overview["Duplicate Rows"]
                )
                col4.metric(
                    "Memory Usage",
                    f'{overview["Memory Usage (KB)"]} KB'
                )

                # Dataset preview
                st.markdown("### Dataset Preview")

                st.dataframe(
                    df.head(10),
                    use_container_width=True
                )

                # Column information
                st.markdown("### Column Information")

                column_report = get_col_info(df)

                st.dataframe(
                    column_report,
                    use_container_width=True
                )

                # Missing values
                st.markdown("### Missing Value Analysis")

                missing_report = get_missing_values(df)

                st.dataframe(
                    missing_report,
                    use_container_width=True
                )

                st.success(
                    f"Successfully analysed {uploaded_file.name}"
                )

elif page == "Exploratory Data Analysis":

    from modules.eda import (
        get_numeric_summary,
        get_categorical_summary,
        get_correlation_matrix
    )

    st.header("Exploratory Data Analysis")
    st.write(
        "Explore statistical patterns, relationships "
        "and distributions in your dataset."
    )

    uploaded_file = st.file_uploader(
        "Upload a CSV dataset for EDA",
        type=["csv"],
        key="eda_upload"
    )

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        st.success("Dataset loaded successfully!")

        # 1. Numerical Analysis
        st.markdown("## Numerical Analysis")

        numeric_summary = get_numeric_summary(df)

        if numeric_summary is not None:
            st.dataframe(numeric_summary, width="stretch")
        else:
            st.info("No numerical columns found.")

        # 2. Categorical Analysis
        st.markdown("## Categorical Analysis")

        categorical_summary = get_categorical_summary(df)

        if categorical_summary is not None:
            st.dataframe(categorical_summary, width="stretch")
        else:
            st.info("No categorical columns found.")

        # 3. Correlation Heatmap
        st.markdown("## Correlation Analysis")

        correlation = get_correlation_matrix(df)

        if correlation is not None:

            import plotly.express as px

            fig = px.imshow(
                correlation,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title="Feature Correlation Heatmap"
            )

            st.plotly_chart(fig, width="stretch")

        else:
            st.info(
                "At least two numerical columns are "
                "required for correlation analysis."
            )

        # 4. Interactive Visualisation
        st.markdown("## Interactive Visualisation")

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical_columns = df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        if numeric_columns:

            selected_column = st.selectbox(
                "Select a numerical column",
                numeric_columns
            )

            fig = px.histogram(
                df,
                x=selected_column,
                title=f"Distribution of {selected_column}",
                marginal="box"
            )

            st.plotly_chart(fig, width="stretch")

        if categorical_columns:

            selected_category = st.selectbox(
                "Select a categorical column",
                categorical_columns
            )

            category_counts = (
                df[selected_category]
                .value_counts()
                .reset_index()
            )

            category_counts.columns = [
                selected_category,
                "Count"
            ]

            fig = px.bar(
                category_counts,
                x=selected_category,
                y="Count",
                title=f"Distribution of {selected_category}"
            )

            st.plotly_chart(fig, width="stretch")

    else:
        st.info("Upload a CSV file to begin exploratory analysis.")

elif page == "AI Data Analyst":
    st.subheader("Conversational AI Data Analyst")
    st.info("Gemini-powered analytics are coming next.")

elif page == "Executive Reports":
    st.subheader("Executive Dossier Generator")
    st.info("Automated report generation is coming next.")