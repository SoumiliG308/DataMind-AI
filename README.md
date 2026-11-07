# 📊 DataMind AI

### Your data. Your questions. Intelligent insights.

**DataMind AI** is an AI-powered data analytics assistant designed to simplify exploratory data analysis and make datasets easier to understand. It combines automated data profiling, statistical analysis, interactive visualisations, LLM-powered natural-language analytics and downloadable executive reports in one workspace.

The goal is to help users move from raw CSV data to meaningful insights without having to perform every analytical step manually.

---

## ✨ Key Features

### 1. 🔍 Data Health Audit
Upload CSV datasets and automatically inspect their structure and quality.

- Dataset overview: rows, columns, duplicates and memory usage.
- Column-level information and data types.
- Missing-value counts and percentages.
- Dataset preview and data-quality observations.

### 2. 📈 Exploratory Data Analysis (EDA)
Explore numerical and categorical features through automated analysis.

- Numerical and categorical statistical summaries.
- Feature correlation analysis with interactive heatmaps.
- IQR-based outlier detection.
- Histograms and box plots.
- Categorical feature distribution visualisations.
- Interactive Plotly charts.

### 3. 🤖 AI Data Analyst
An LLM-powered analytical assistant that allows users to explore datasets using natural-language questions.

- Ask questions about uploaded datasets.
- Translate analytical questions into structured tool calls.
- Perform data-backed analysis using approved Python/Pandas functions.
- Generate relevant charts and visualisations.
- Receive explanations of analytical results.
- Conversational follow-ups and chat experience (under development/testing).

The analytical computations are performed using Python-based tools, while the language model helps interpret questions and communicate the findings.

### 4. 📑 Executive Dossier Generator
Generate downloadable reports containing important dataset insights.

- Dataset statistics and overview.
- Data-quality findings.
- Numerical and categorical summaries.
- Correlation analysis.
- Outlier observations.
- Automatically generated executive findings.
- Export reports in **PDF and Markdown** formats.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend / Application | Streamlit |
| Data Processing | Pandas, NumPy |
| Data Visualisation | Plotly |
| Machine Learning / Analytics | Scikit-learn and statistical methods |
| LLM Integration | OpenRouter |
| PDF Generation | ReportLab |
| Development Environment | VS Code, Git, GitHub |

---

## 🏗️ Project Structure

```text
DataMind-AI/
│
├── app.py
├── requirements.txt
├── README.md
│
├── modules/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_quality.py
│   ├── eda.py
│   ├── analytics_tools.py
│   ├── llm_engine.py
│   └── report_generator.py
│
├── sample_data/
│
├── assets/
│
└── .streamlit/
    └── secrets.toml
```

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- An OpenRouter API key for AI-powered functionality

### 1. Clone the repository

```bash
git clone https://github.com/SoumiliG308/DataMind-AI.git
```

### 2. Navigate to the project directory

```bash
cd DataMind-AI
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API credentials

Create a directory named `.streamlit` in the project root, and inside it create `secrets.toml`.

Add your OpenRouter API key:

```toml
OPENROUTER_API_KEY = "your_api_key_here"
```

**Important:** Never upload your API key or `secrets.toml` file to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🔐 Security and Data Handling

- API credentials are stored separately using Streamlit secrets.
- API keys should never be committed to version control.
- AI-generated analytical operations are restricted to predefined tools rather than arbitrary generated Python execution.

---

## 🚧 Development Status

DataMind AI is currently under active development.

| Component | Status |
|---|---|
| Data Health Audit | Implemented |
| Exploratory Data Analysis | Implemented |
| AI Data Analyst | Implemented; conversational experience and live API validation in progress |
| Executive Report Generator | Implemented |
| UI Refinement | In progress |
| Deployment | Planned |

The AI module's live behaviour and provider availability are subject to API limits and testing.

---

## 🎯 Project Objective

DataMind AI aims to make data analytics more accessible by combining automated exploratory analysis with natural-language interaction.

Instead of manually navigating multiple analytical tools, users can upload a dataset, investigate its characteristics, explore patterns and generate structured reports through a unified interface.

---

## 👩‍💻 Author

**Soumili Ghosh**
GitHub: [@SoumiliG308](https://github.com/SoumiliG308)

---

*Built with Python, data analytics and a curiosity for making data more understandable.*