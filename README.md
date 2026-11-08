# DataMind AI
### AI-Powered Data Analytics and Natural Language Insights Platform

**DataMind AI** is an interactive, LLM-powered data analytics platform designed to simplify the process of exploring, understanding and interpreting structured datasets. It enables users to upload CSV files, perform exploratory data analysis, identify data quality issues, and generate meaningful insights through natural-language queries.

By combining traditional data analysis techniques with Large Language Models (LLMs), DataMind AI bridges the gap between raw data and actionable insights. Users can interact with their datasets conversationally, explore patterns through interactive visualizations, and generate structured analytical reports without manually performing every analysis.

🌐 **Live Demo:** [DataMind AI](https://datamind-ai-analytics.streamlit.app/)  
💻 **GitHub Repository:** [DataMind-AI](https://github.com/SoumiliG308/DataMind-AI)

---

## Key Features

**1. Data Health Audit**
- Upload and inspect CSV datasets.
- Identify missing values, duplicate records and data types.
- Examine dataset structure, memory usage and data quality.

**2. Exploratory Data Analysis (EDA)**
- Generate descriptive statistical summaries.
- Analyse numerical correlations and potential outliers.
- Explore data through interactive Plotly visualizations.

**3. AI Data Analyst**
- Ask questions about datasets using natural language.
- Perform analytical operations through predefined data-analysis tools.
- Generate data-driven explanations, comparisons and visual insights using an LLM.

**4. Executive Reports**
- Generate structured analytical reports.
- Summarize important findings and dataset observations.
- Export reports in PDF format.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend & Framework | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| LLM Integration | OpenRouter API |
| Report Generation | ReportLab |
| Deployment | Streamlit Community Cloud |

## Project Structure

```text
DataMind-AI/
├── app.py
├── modules/
│   ├── data_loader.py
│   ├── data_quality.py
│   ├── eda.py
│   ├── analytics_tools.py
│   ├── llm_engine.py
│   └── report_generator.py
├── sample_data/
├── assets/
├── requirements.txt
└── README.md
```

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/SoumiliG308/DataMind-AI.git
cd DataMind-AI
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure API credentials**

Create `.streamlit/secrets.toml` and add your OpenRouter API key:

```toml
OPENROUTER_API_KEY = "your_api_key"
```

**4. Run the application**

```bash
streamlit run app.py
```

*Security note: Keep API credentials private. Never commit `secrets.toml` to the repository.*

---

## Author

**Soumili Ghosh**  
B.Tech – Computer Science and Engineering (Data Science)

[GitHub Profile](https://github.com/SoumiliG308)

---

*DataMind AI — Transforming raw datasets into meaningful insights through intelligent analytics.*