import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import re
import hashlib
from modules.llm_engine import run_data_analyst
from modules.report_generator import generate_pdf_report, generate_markdown_report

st.set_page_config(
    page_title="DataMind AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------
# CUSTOM UI STYLING
# --------------------------------

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    [data-testid="stSidebar"] {
        background-color: #171923;
        border-right: 1px solid #303443;
    }

    [data-testid="stSidebar"] h1 {
        color: #8B9CFF;
    }

    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
    }

    .hero h1 {
        font-size: 2.8rem;
        font-weight: 750;
        margin-bottom: 0.4rem;
    }

    .hero p {
        color: #A5AEC5;
        font-size: 1.05rem;
    }

    .metric-card {
        background: linear-gradient(145deg, #22283A, #1B2030);
        border: 1px solid #343C55;
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }

    .metric-label {
        color: #A5AEC5;
        font-size: 0.9rem;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.3rem;
    }

    .module-card {
        background: #1D2230;
        border: 1px solid #343C55;
        border-radius: 14px;
        padding: 1.3rem;
        min-height: 180px;
        margin-bottom: 1rem;
        transition: 0.2s ease;
    }

    .module-card:hover {
        border-color: #8494FF;
        background: #252C40;
    }

    .module-card h3 {
        color: #E7EBFF;
        font-size: 1.1rem;
    }

    .module-card p {
        color: #A5AEC5;
        font-size: 0.9rem;
    }

    div[data-testid="stMetric"] {
        background: #1D2230;
        border: 1px solid #343C55;
        padding: 1rem;
        border-radius: 12px;
    }

    div.stButton > button {
        border-radius: 9px;
        border: 1px solid #6478E8;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #A1AEFF;
        color: #A1AEFF;
    }

    h1, h2, h3 {
        letter-spacing: -0.4px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------
# SIDEBAR & NAVIGATION
# --------------------------------

pages = [
    "Dashboard",
    "Data Health Audit",
    "Exploratory Data Analysis",
    "AI Data Analyst",
    "Executive Reports"
]

if "selected_module" not in st.session_state:
    st.session_state["selected_module"] = "Dashboard"


def navigate_to_module(module_name):
    st.session_state["selected_module"] = module_name


with st.sidebar:

    st.markdown("## 📊 DataMind AI")
    st.caption("Intelligent Analytics Workspace")

    st.divider()

    if st.session_state["selected_module"] == "Dashboard":

        st.markdown("### Welcome!")
        st.caption("Choose a module from your dashboard to get started.")

    else:

        st.markdown("### Navigation")

        st.radio(
            "Choose a module",
            pages,
            key="selected_module"
        )

    st.divider()

    st.caption("Version 1.0 | Development Build")


page = st.session_state["selected_module"]

# --------------------------------
# DASHBOARD
# --------------------------------


if page == "Dashboard":

    # Centre welcome section
    st.markdown("""
        <div class="hero">
            <h1>📊 DataMind AI</h1>
            <p>Your data. Your questions. Intelligent insights.</p>
        </div>
    """, unsafe_allow_html=True)

    # Overview metrics
    col1, col2, col3 = st.columns(3)

    metrics = [
        ("MODULES", "04"),
        ("DATASETS", "CSV Files. Ready to upload"),
        ("VERSION", "1.0")
    ]

    for col, (label, value) in zip(
        [col1, col2, col3], metrics
    ):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("## Explore your workspace")
    st.caption("Choose a module to get started.")

    # Module cards
    modules = [
        (
            "🔍 Data Health Audit",
            "Inspect dataset structure, missing values, "
            "data types and duplicate records.",
            "Data Health Audit"
        ),
        (
            "📈 Exploratory Data Analysis",
            "Explore statistics, correlations, outliers "
            "and interactive visualisations.",
            "Exploratory Data Analysis"
        ),
        (
            "🤖 AI Data Analyst",
            "Ask questions in natural language and "
            "receive data-backed analytical insights.",
            "AI Data Analyst"
        ),
        (
            "📑 Executive Reports",
            "Generate and download comprehensive "
            "Markdown and PDF reports.",
            "Executive Reports"
        )
    ]

    col1, col2 = st.columns(2)

    for index, (title, description, target) in enumerate(modules):
        current_col = col1 if index % 2 == 0 else col2

        with current_col:
            with st.container(border=True):
                st.markdown(f"### {title}")
                st.write(description)

                if st.button(
                    f"Open {target} →",
                    key=f"open_{index}",
                    use_container_width=True,
                    on_click=navigate_to_module,
                    args=(target,)
                ):
                    st.session_state["selected_module"] = target
                    st.rerun()


elif page == "Data Health Audit":

    from modules.data_loader import load_csv
    from modules.data_quality import (
        get_dataset_overview,
        get_missing_values,
        get_col_info
    )

    st.header("🔍 Data Health Audit")
    st.caption("Inspect dataset structure and identify potential data-quality issues.")

    uploaded_files = st.file_uploader(
        "Upload CSV datasets",
        type=["csv"],
        accept_multiple_files=True,
        key="health_upload"
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            with st.container(border=True):

                st.subheader(f"📄 {uploaded_file.name}")

                df = load_csv(uploaded_file)

                if df is None:
                    continue

                overview = get_dataset_overview(df)
                missing_report = get_missing_values(df)
                column_report = get_col_info(df)

                # Overview metrics
                st.markdown("#### Dataset Overview")

                c1, c2, c3, c4 = st.columns(4)

                c1.metric("Total Rows", f'{overview["Rows"]:,}')
                c2.metric("Total Columns", overview["Columns"])
                c3.metric("Duplicate Rows", overview["Duplicate Rows"])
                c4.metric(
                    "Memory Usage",
                    f'{overview["Memory Usage (KB)"]:.2f} KB'
                )

                # Organised dataset sections
                tab1, tab2, tab3 = st.tabs([
                    "📋 Preview",
                    "🧩 Column Information",
                    "⚠️ Missing Values"
                ])

                with tab1:

                    st.markdown("**First 10 records**")

                    st.dataframe(
                        df.head(10),
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        f"Showing 10 of {len(df):,} records."
                    )

                with tab2:

                    st.dataframe(
                        column_report,
                        use_container_width=True,
                        hide_index=True
                    )

                with tab3:

                    total_missing = int(
                        missing_report["Missing Values"].sum()
                    )

                    missing_percentage = (
                        total_missing / (df.shape[0] * df.shape[1]) * 100
                        if df.size else 0
                    )

                    m1, m2 = st.columns(2)

                    m1.metric("Missing Cells", f"{total_missing:,}")
                    m2.metric(
                        "Overall Missing Percentage",
                        f"{missing_percentage:.2f}%"
                    )

                    if total_missing > 0:

                        missing_display = missing_report[
                            missing_report["Missing Values"] > 0
                        ].sort_values(
                            "Missing Percentage (%)",
                            ascending=False
                        )

                        st.dataframe(
                            missing_display,
                            use_container_width=True
                        )

                        fig = px.bar(
                            missing_display.reset_index(),
                            x="index",
                            y="Missing Percentage (%)",
                            title="Missing Values by Column",
                            labels={"index": "Column"},
                            color="Missing Percentage (%)",
                            color_continuous_scale="Blues"
                        )
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"missing_{uploaded_file.name}"
                        )

                    else:

                        st.success(
                            "Excellent! No missing values were detected."
                        )

                st.success(
                    f"Successfully analysed {uploaded_file.name}"
                )

    else:

        st.info("Upload one or more CSV files to begin the health audit.")


elif page == "Exploratory Data Analysis":

    from modules.eda import (
        get_numeric_summary,
        get_categorical_summary,
        get_correlation_matrix,
        get_outlier_summary,
        get_outlier_records,
        get_identifier_columns,
        get_binary_numeric_columns,
        get_numeric_columns,
        get_categorical_columns,
        get_default_outlier_exclusions
    )

    st.header("📈 Exploratory Data Analysis")
    st.caption("Discover distributions, relationships and potential anomalies in your data.")

    uploaded_file = st.file_uploader(
        "Upload a CSV dataset for analysis",
        type=["csv"],
        key="eda_upload"
    )

    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.astype(str).str.strip()

            if df.empty or len(df.columns) == 0:
                st.error("The uploaded dataset is empty.")
            else:
                identifier_columns = get_identifier_columns(df)
                binary_columns = get_binary_numeric_columns(df)
                numeric_columns = get_numeric_columns(df)
                categorical_columns = get_categorical_columns(df)

                st.success(f"Dataset loaded: {uploaded_file.name}")

                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", f"{df.shape[0]:,}")
                c2.metric("Columns", df.shape[1])
                c3.metric("Analytical Numeric Features", len(numeric_columns))

                with st.expander("⚙️ Analysis settings", expanded=False):
                    st.caption(
                        "DataMind AI automatically identifies likely record IDs and "
                        "high-cardinality text columns. These are excluded from default "
                        "analysis to avoid misleading charts. You can include them below."
                    )
                    include_ids_in_stats = st.checkbox(
                        "Include likely identifier columns in statistical summaries",
                        value=False,
                        key="eda_include_ids_stats"
                    )
                    include_ids_in_correlation = st.checkbox(
                        "Include likely identifier columns in correlation analysis",
                        value=False,
                        key="eda_include_ids_corr"
                    )
                    include_high_cardinality = st.checkbox(
                        "Include high-cardinality text columns in category charts",
                        value=False,
                        key="eda_include_high_cardinality"
                    )

                    if identifier_columns:
                        st.caption("Likely identifiers: " + ", ".join(map(str, identifier_columns)))
                    if binary_columns:
                        st.caption("Binary numeric columns (excluded from IQR by default): "
                                   + ", ".join(map(str, binary_columns)))

                if include_ids_in_stats:
                    numeric_summary_columns = df.select_dtypes(include="number").columns.tolist()
                    categorical_summary_columns = df.select_dtypes(
                        include=["object", "category", "bool"]
                    ).columns.tolist()
                else:
                    numeric_summary_columns = numeric_columns
                    categorical_summary_columns = categorical_columns

                if include_high_cardinality:
                    chart_categorical_columns = df.select_dtypes(
                        include=["object", "category", "bool"]
                    ).columns.tolist()
                else:
                    chart_categorical_columns = categorical_columns

                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Statistical Summary",
                    "🔗 Correlation",
                    "🚨 Outlier Detection",
                    "📉 Visualisation"
                ])

                with tab1:
                    st.subheader("Numerical Analysis")
                    numeric_summary = (
                        df[numeric_summary_columns].describe().T
                        if numeric_summary_columns else None
                    )
                    if numeric_summary is not None:
                        numeric_summary["median"] = df[numeric_summary_columns].median()
                        numeric_summary["missing_values"] = df[numeric_summary_columns].isnull().sum()
                        st.dataframe(numeric_summary.round(2), use_container_width=True)
                    else:
                        st.info("No suitable numerical columns found.")

                    st.divider()
                    st.subheader("Categorical Analysis")
                    categorical_summary = get_categorical_summary(
                        df[categorical_summary_columns],
                        include_identifiers=True
                    ) if categorical_summary_columns else None

                    if categorical_summary is not None:
                        st.dataframe(categorical_summary, use_container_width=True)
                    else:
                        st.info("No suitable categorical columns found.")

                with tab2:
                    st.subheader("Feature Correlation Heatmap")
                    correlation = get_correlation_matrix(
                        df, include_identifiers=include_ids_in_correlation
                    )
                    if correlation is not None:
                        fig = px.imshow(
                            correlation,
                            text_auto=True,
                            aspect="auto",
                            color_continuous_scale="RdBu_r",
                            title="Numerical Feature Correlations",
                            zmin=-1,
                            zmax=1
                        )
                        st.plotly_chart(
                            fig, use_container_width=True, key="eda_correlation"
                        )
                        st.caption(
                            "Binary outcome columns (such as Exited) remain included. "
                            "Likely identifiers are excluded by default. Correlation "
                            "does not necessarily imply causation."
                        )
                    else:
                        st.info(
                            "At least two suitable numerical columns are required "
                            "for correlation analysis."
                        )

                with tab3:
                    st.subheader("IQR-Based Outlier Detection")
                    all_numeric_columns = df.select_dtypes(include="number").columns.tolist()

                    if all_numeric_columns:
                        default_exclusions = get_default_outlier_exclusions(df)
                        exclude_columns = st.multiselect(
                            "Exclude columns from outlier detection",
                            options=all_numeric_columns,
                            default=default_exclusions,
                            help=(
                                "Likely IDs and binary flags are excluded by default. "
                                "You can change the selection. Consider excluding "
                                "encoded categories and discrete count fields when "
                                "the IQR rule is not meaningful for them."
                            ),
                            key="eda_exclude_columns"
                        )
                        available_columns = [
                            col for col in all_numeric_columns if col not in exclude_columns
                        ]
                        outlier_report = get_outlier_summary(
                            df, exclude_columns=exclude_columns
                        )

                        if outlier_report is not None and not outlier_report.empty:
                            st.dataframe(
                                outlier_report, use_container_width=True, hide_index=True
                            )
                            total_outliers = int(outlier_report["Outlier Count"].sum())
                            st.metric("Total Potential Outlier Flags", f"{total_outliers:,}")
                            st.caption(
                                "The 1.5 × IQR rule identifies potential outliers, not "
                                "confirmed errors. Flags are not automatically removed."
                            )

                            if available_columns:
                                st.divider()
                                st.markdown("#### Inspect Outlier Records")
                                selected_records_column = st.selectbox(
                                    "Choose a numerical column",
                                    available_columns,
                                    key="outlier_records_column"
                                )
                                outlier_records = get_outlier_records(
                                    df, selected_records_column
                                )
                                st.metric("Records Identified", len(outlier_records))

                                if not outlier_records.empty:
                                    st.dataframe(outlier_records, use_container_width=True)
                                    csv_data = outlier_records.to_csv(index=False).encode("utf-8")
                                    st.download_button(
                                        "⬇️ Download Outlier Records",
                                        data=csv_data,
                                        file_name=f"{selected_records_column}_outliers.csv",
                                        mime="text/csv",
                                        key="outlier_download"
                                    )
                                else:
                                    st.success("No outlier records found in this column.")

                                st.divider()
                                st.markdown("#### Outlier Box Plot")
                                selected_box_column = st.selectbox(
                                    "Select a column to visualise",
                                    available_columns,
                                    key="outlier_boxplot_column"
                                )
                                fig = px.box(
                                    df, y=selected_box_column, points="outliers",
                                    title=f"Distribution of {selected_box_column}"
                                )
                                st.plotly_chart(
                                    fig, use_container_width=True, key="outlier_boxplot"
                                )
                            else:
                                st.info("All numerical columns have been excluded.")
                        else:
                            st.info("No eligible numerical columns are available for IQR analysis.")
                    else:
                        st.info("No numerical columns found.")

                with tab4:
                    st.subheader("Explore Your Features")

                    if numeric_columns:
                        st.markdown("#### Numerical Feature Distribution")
                        selected_column = st.selectbox(
                            "Select a numerical column",
                            numeric_columns,
                            key="eda_numeric_visual"
                        )
                        chart_type = st.radio(
                            "Choose visualisation",
                            ["Histogram", "Box Plot"],
                            horizontal=True,
                            key="eda_numeric_chart"
                        )
                        if chart_type == "Box Plot":
                            fig = px.box(
                                df, y=selected_column,
                                title=f"Box Plot: {selected_column}"
                            )
                        else:
                            fig = px.histogram(
                                df, x=selected_column, marginal="box",
                                title=f"Distribution of {selected_column}"
                            )
                        st.plotly_chart(
                            fig, use_container_width=True, key="eda_numeric_plot"
                        )
                    else:
                        st.info("No suitable numerical columns available for visualisation.")

                    if chart_categorical_columns:
                        st.divider()
                        st.markdown("#### Categorical Feature Distribution")
                        selected_category = st.selectbox(
                            "Select a categorical column",
                            chart_categorical_columns,
                            key="eda_category_visual"
                        )
                        category_counts = (
                            df[selected_category].astype("string")
                            .fillna("(Missing)")
                            .value_counts()
                            .head(20)
                            .rename_axis(selected_category)
                            .reset_index(name="Count")
                        )
                        fig = px.bar(
                            category_counts,
                            x=selected_category,
                            y="Count",
                            title=f"Top 20 Categories: {selected_category}"
                        )
                        fig.update_layout(
                            xaxis_title=selected_category,
                            yaxis_title="Count"
                        )
                        st.plotly_chart(
                            fig, use_container_width=True, key="eda_category_plot"
                        )
                        if df[selected_category].nunique(dropna=True) > 20:
                            st.caption(
                                "Showing the 20 most frequent categories to keep "
                                "the chart readable."
                            )
                    else:
                        st.info(
                            "No suitable categorical columns found. Enable high-cardinality "
                            "text columns in Analysis settings if you want to inspect them."
                        )

        except Exception as error:
            st.error(f"Unable to analyse the dataset: {error}")
    else:
        st.info("Upload a CSV file to begin exploratory analysis.")


elif page == "AI Data Analyst":

    st.header("🤖 Conversational AI Data Analyst")
    st.caption(
        "Ask questions about your uploaded dataset. DataMind AI uses approved "
        "analytical tools to calculate results and explain them."
    )

    uploaded_file = st.file_uploader(
        "Upload a CSV dataset",
        type=["csv"],
        key="ai_analyst_upload"
    )

    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()
            fingerprint = hashlib.sha256(file_bytes).hexdigest()
            if st.session_state.get("ai_dataset_fingerprint") != fingerprint:
                df_new = pd.read_csv(uploaded_file)
                df_new.columns = df_new.columns.astype(str).str.strip()

                if df_new.empty or len(df_new.columns) == 0:
                    st.error("The uploaded dataset is empty.")
                    st.stop()

                st.session_state["ai_dataset"] = df_new
                st.session_state["ai_dataset_name"] = uploaded_file.name
                st.session_state["ai_dataset_fingerprint"] = fingerprint
                st.session_state["ai_messages"] = []
        except Exception as error:
            st.error(f"Unable to load dataset: {error}")

    df = st.session_state.get("ai_dataset")

    if df is not None:
        st.success(
            f"Dataset ready: {st.session_state.get('ai_dataset_name', 'Uploaded CSV')}"
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", f"{df.shape[0]:,}")
        col2.metric("Columns", df.shape[1])
        col3.metric("Conversation turns", len(st.session_state.get("ai_messages", [])) // 2)

        with st.expander("Preview dataset"):
            st.dataframe(df.head(10), use_container_width=True)

        if "ai_messages" not in st.session_state:
            st.session_state["ai_messages"] = []

        top_left, top_right = st.columns([4, 1])
        with top_left:
            st.markdown("### Chat with your dataset")
        with top_right:
            if st.button("＋ New chat", use_container_width=True):
                st.session_state["ai_messages"] = []
                st.rerun()

        # Render the existing conversation, including any charts returned
        # by the analytical chart tool for each assistant turn.
        for message_index, chat_item in enumerate(st.session_state["ai_messages"]):
            with st.chat_message(chat_item["role"]):
                st.markdown(chat_item["content"])

                if chat_item["role"] == "assistant":
                    debug_log = chat_item.get("debug", [])
                    chart_items = [
                        item for item in debug_log
                        if item.get("tool") == "generate_chart"
                    ]

                    # Defensive guard: one assistant turn should display at
                    # most one chart, even if a provider returns duplicates.
                    for chart_index, item in enumerate(chart_items[-1:]):
                        spec = item.get("result", {})
                        if not isinstance(spec, dict) or "error" in spec:
                            if isinstance(spec, dict):
                                st.warning(spec.get("error", "Unable to create chart."))
                            continue

                        chart_type = spec.get("chart_type")
                        x = spec.get("x_column")
                        y = spec.get("y_column")
                        aggregation = spec.get("aggregation", "mean")

                        try:
                            if chart_type == "histogram":
                                fig = px.histogram(df, x=x, title=spec.get("title"))
                            elif chart_type == "scatter":
                                fig = px.scatter(df, x=x, y=y, title=spec.get("title"))
                            elif chart_type == "box":
                                fig = px.box(df, y=y, title=spec.get("title"))
                            elif chart_type == "bar":
                                if aggregation == "count":
                                    chart_data = (
                                        df.groupby(x, dropna=False)
                                        .size()
                                        .reset_index(name="Count")
                                    )
                                    fig = px.bar(
                                        chart_data, x=x, y="Count",
                                        title=spec.get("title")
                                    )
                                else:
                                    chart_data = (
                                        df.groupby(x, dropna=False)[y]
                                        .agg(aggregation)
                                        .reset_index()
                                    )
                                    fig = px.bar(
                                        chart_data, x=x, y=y,
                                        title=spec.get("title")
                                    )
                            else:
                                continue
                            if chart_type == "bar" and y == "Exited":
                                fig.update_layout(yaxis_title="Churn Rate")

                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                                key=f"ai_chart_{message_index}_{chart_index}"
                            )
                        except Exception as chart_error:
                            st.warning(f"Chart could not be rendered: {chart_error}")


        question = st.chat_input("Ask a question about your data...")

        if question:
            previous_messages = [
                {"role": item["role"], "content": item["content"]}
                for item in st.session_state["ai_messages"]
            ]
            st.session_state["ai_messages"].append({
                "role": "user",
                "content": question
            })

            with st.spinner("DataMind AI is analysing your dataset..."):
                result = run_data_analyst(
                    df,
                    question,
                    history=previous_messages
                )


            if isinstance(result, dict):
                answer = result.get("answer", "No answer was returned.")
                debug_log = result.get("debug", [])

                # Remove broken image Markdown from the AI response
                answer = re.sub(
                    r'!\[[^\]]*\]\([^)]+\)',
                    '',
                    answer
                )
            else:
                answer = str(result)
                debug_log = []

            st.session_state["ai_messages"].append({
                "role": "assistant",
                "content": answer,
                "debug": debug_log
            })
            st.rerun()

    else:
        st.info("Upload a CSV file to start a conversation with DataMind AI.")


elif page == "Executive Reports":

    from modules.report_generator import (
        generate_pdf_report,
        generate_markdown_report,
        collect_report_data,
        generate_executive_findings
    )

    st.header("📑 Executive Dossier Generator")
    st.caption(
        "Turn your dataset analysis into a structured, downloadable report."
    )

    uploaded_file = st.file_uploader(
        "Upload a CSV dataset",
        type=["csv"],
        key="report_upload"
    )

    if uploaded_file is not None:

        try:

            file_bytes = uploaded_file.getvalue()
            file_fingerprint = hashlib.sha256(file_bytes).hexdigest()

            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.astype(str).str.strip()

            if df.empty or len(df.columns) == 0:

                st.error("The uploaded dataset is empty.")

            else:

                st.success(f"Dataset loaded: {uploaded_file.name}")

                # Dataset overview
                c1, c2, c3 = st.columns(3)

                c1.metric("Total Records", f"{df.shape[0]:,}")
                c2.metric("Total Features", df.shape[1])
                c3.metric(
                    "Duplicate Rows",
                    f"{int(df.duplicated().sum()):,}"
                )

                with st.expander("👀 Preview Dataset"):

                    st.dataframe(
                        df.head(10),
                        use_container_width=True,
                        hide_index=True
                    )

                st.divider()

                st.subheader("Generate Your Executive Report")

                st.write(
                    "The report includes dataset statistics, "
                    "data-quality findings, EDA summaries and "
                    "automatically generated observations."
                )

                if st.button(
                    "✨ Generate Executive Report",
                    type="primary",
                    use_container_width=True,
                    key="generate_report"
                ):

                    with st.spinner(
                        "Preparing your executive dossier..."
                    ):

                        try:

                            report_data = collect_report_data(df)

                            findings = generate_executive_findings(
                                report_data
                            )

                            markdown_report = generate_markdown_report(df)
                            pdf_report = generate_pdf_report(df)

                            st.session_state["report_fingerprint"] = (
                                file_fingerprint
                            )

                            st.session_state["report_markdown"] = (
                                markdown_report
                            )

                            st.session_state["report_pdf"] = pdf_report

                            st.session_state["report_findings"] = findings

                            st.success(
                                "Your executive report is ready!"
                            )

                        except Exception as error:

                            st.error(
                                f"Report generation failed: {error}"
                            )

                # Display report only if it belongs to the current dataset.
                report_is_ready = (
                    st.session_state.get("report_fingerprint")
                    == file_fingerprint
                    and st.session_state.get("report_markdown") is not None
                    and st.session_state.get("report_pdf") is not None
                )

                if report_is_ready:

                    st.divider()

                    st.success("Executive dossier successfully generated.")

                    report_tab1, report_tab2 = st.tabs([
                        "💡 Key Findings",
                        "📖 Report Preview"
                    ])

                    with report_tab1:

                        st.subheader("Executive Findings")

                        findings = st.session_state.get(
                            "report_findings",
                            []
                        )

                        if findings:

                            for index, finding in enumerate(findings, 1):

                                st.markdown(
                                    f"**{index}.** {finding}"
                                )

                        else:

                            st.info(
                                "No executive findings were generated."
                            )

                    with report_tab2:

                        st.markdown("#### Markdown Report")

                        with st.container(border=True):

                            st.markdown(
                                st.session_state["report_markdown"]
                            )

                    st.divider()

                    st.subheader("Download Your Report")

                    download_col1, download_col2 = st.columns(2)

                    with download_col1:

                        st.download_button(
                            label="⬇️ Download PDF",
                            data=st.session_state["report_pdf"],
                            file_name="DataMind_Executive_Report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="download_pdf"
                        )

                    with download_col2:

                        st.download_button(
                            label="⬇️ Download Markdown",
                            data=st.session_state["report_markdown"],
                            file_name="DataMind_Executive_Report.md",
                            mime="text/markdown",
                            use_container_width=True,
                            key="download_markdown"
                        )

        except Exception as error:

            st.error(f"Unable to process the dataset: {error}")

    else:

        st.info(
            "Upload a CSV file to generate your executive dossier."
        )
