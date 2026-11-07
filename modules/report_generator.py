import pandas as pd
import numpy as np

from modules.data_quality import (
    get_dataset_overview,
    get_missing_values,
    get_col_info
)

from modules.eda import (
    get_numeric_summary,
    get_categorical_summary,
    get_correlation_matrix,
    get_outlier_summary
)

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table, LongTable,
    TableStyle,
    PageBreak
)

def collect_report_data(df):
    """
    Collect all important dataset statistics
    required for the executive report.
    """

    report_data = {}

    # 1. Dataset overview
    report_data["overview"] = get_dataset_overview(df)

    # 2. Missing value analysis
    report_data["missing_values"] = get_missing_values(df)

    # 3. Column information
    report_data["column_info"] = get_col_info(df)

    # 4. Numerical statistics
    report_data["numeric_summary"] = get_numeric_summary(df)

    # 5. Categorical statistics
    report_data["categorical_summary"] = get_categorical_summary(df)

    # Avoid presenting arbitrary modes for high-cardinality columns
    # (for example, an Address column where nearly every value is unique).
    categorical_summary = report_data["categorical_summary"]
    if categorical_summary is not None and not categorical_summary.empty:
        for column in categorical_summary.index:
            unique_count = int(categorical_summary.loc[column, "Unique Values"])
            non_null_count = int(df[column].notna().sum())

            if (
                non_null_count > 0
                and unique_count >= 20
                and unique_count / non_null_count >= 0.5
            ):
                categorical_summary.loc[column, "Most Frequent"] = (
                    "High cardinality — mode omitted"
                )

    # 6. Correlation analysis
    report_data["correlation_matrix"] = get_correlation_matrix(df)

    # 7. Outlier analysis
    report_data["outlier_summary"] = get_outlier_summary(df)

    return report_data

def generate_executive_findings(report_data):
    """
    Generate factual observations from collected dataset statistics.
    """

    findings = []

    # 1. Dataset size
    overview = report_data["overview"]

    findings.append(
        f"The dataset contains {overview['Rows']} rows "
        f"and {overview['Columns']} columns."
    )

    # 2. Duplicate records
    duplicates = overview["Duplicate Rows"]

    if duplicates > 0:
        findings.append(
            f"{duplicates} duplicate rows were detected."
        )
    else:
        findings.append("No duplicate rows were detected.")

    # 3. Missing values
    missing_df = report_data["missing_values"]

    if not missing_df.empty:
        highest_missing_column = (
            missing_df["Missing Percentage (%)"].idxmax()
        )

        highest_missing_percentage = (
            missing_df.loc[
                highest_missing_column,
                "Missing Percentage (%)"
            ]
        )

        if highest_missing_percentage > 0:
            findings.append(
                f"'{highest_missing_column}' has the highest "
                f"missing-value percentage at "
                f"{highest_missing_percentage}%."
            )
        else:
            findings.append("No missing values were detected.")

    # 4. Outlier observations
    outlier_df = report_data["outlier_summary"]

    if outlier_df is not None and not outlier_df.empty:

        highest_outlier_index = (
            outlier_df["Outlier Percentage (%)"].idxmax()
        )

        highest_outlier_column = (
            outlier_df.loc[
                highest_outlier_index,
                "Column"
            ]
        )

        highest_outlier_percentage = (
            outlier_df.loc[
                highest_outlier_index,
                "Outlier Percentage (%)"
            ]
        )

        if highest_outlier_percentage > 0:
            findings.append(
                f"'{highest_outlier_column}' has the highest "
                f"IQR-based outlier percentage at "
                f"{highest_outlier_percentage}%."
            )
        else:
            findings.append("No IQR-based outliers were detected.")

    # 5. Correlation observations
    corr = report_data["correlation_matrix"]

    if corr is not None and corr.shape[0] >= 2:

        corr_values = corr.abs().copy()

        # Remove self-correlations.
        for column in corr_values.columns:
            corr_values.loc[column, column] = 0
        strongest_pair = corr_values.stack().idxmax()

        col_a, col_b = strongest_pair

        correlation_value = corr.loc[col_a, col_b]

        findings.append(
            f"The strongest absolute correlation detected is "
            f"between '{col_a}' and '{col_b}', "
            f"with a correlation coefficient of "
            f"{correlation_value:.2f}."
        )
    return findings


def dataframe_to_markdown(dataframe):
    """
    Convert a Pandas DataFrame into a Markdown table
    without requiring an additional package.
    """

    if dataframe is None or dataframe.empty:
        return "No data available."

    display_df = dataframe.copy()

    # Preserve meaningful row labels, such as column names.
    if not isinstance(display_df.index, pd.RangeIndex):
        display_df.insert(0, "Column", display_df.index.astype(str))

    headers = [str(col) for col in display_df.columns]

    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |"
    ]

    for _, row in display_df.iterrows():
        values = []

        for value in row:
            if pd.isna(value):
                value = "N/A"
            elif isinstance(value, (float, np.floating)):
                value = round(float(value), 2)

            # Prevent pipe characters from breaking the table.
            values.append(str(value).replace("|", "\\|"))

        table.append("| " + " | ".join(values) + " |")

    return "\n".join(table)

def generate_markdown_report(df):
    """
    Generate a complete Markdown executive report
    from the uploaded dataset.
    """

    report_data = collect_report_data(df)
    findings = generate_executive_findings(report_data)

    report = []

    report.append("# DataMind AI — Executive Data Report")
    report.append("")
    report.append("## 1. Dataset Overview")
    report.append("")
    report.append(dataframe_to_markdown(
        pd.DataFrame([report_data["overview"]])
    ))

    report.append("")
    report.append("## 2. Executive Findings")
    report.append("")

    for finding in findings:
        report.append(f"- {finding}")

    report.append("")
    report.append("## 3. Data Quality Analysis")
    report.append("")
    report.append("### Missing Values")
    report.append(dataframe_to_markdown(
        report_data["missing_values"]
    ))

    report.append("")
    report.append("### Column Information")
    report.append(dataframe_to_markdown(
        report_data["column_info"]
    ))

    report.append("")
    report.append("## 4. Exploratory Data Analysis")
    report.append("")
    report.append("### Numerical Summary")
    report.append(dataframe_to_markdown(
        report_data["numeric_summary"]
    ))

    report.append("")
    report.append("### Categorical Summary")
    report.append(dataframe_to_markdown(
        report_data["categorical_summary"]
    ))

    report.append("")
    report.append("### Correlation Matrix")
    report.append(dataframe_to_markdown(
        report_data["correlation_matrix"]
    ))

    report.append("")
    report.append("## 5. Outlier Analysis")
    report.append("")
    report.append(dataframe_to_markdown(
        report_data["outlier_summary"]
    ))

    report.append("")
    report.append("---")
    report.append("*Generated automatically by DataMind AI.*")

    return "\n".join(report)



def generate_pdf_report(df):
    """
    Generate a readable, landscape PDF executive report.
    Returns PDF content as bytes.
    """

    from xml.sax.saxutils import escape

    report_data = collect_report_data(df)
    findings = generate_executive_findings(report_data)

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=21,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#243B64"),
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#243B64"),
        spaceBefore=12,
        spaceAfter=7
    )

    subheading_style = ParagraphStyle(
        "SubHeading",
        parent=styles["Heading3"],
        fontSize=10,
        textColor=colors.HexColor("#344563"),
        spaceBefore=8,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        spaceAfter=3
    )

    header_cell_style = ParagraphStyle(
        "TableHeader",
        parent=body_style,
        fontSize=7,
        leading=8,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=body_style,
        fontSize=6.5,
        leading=8,
        wordWrap="CJK"
    )

    story = []

    # Format numbers without unnecessary decimal places.
    def format_value(value):

        if pd.isna(value):
            return "N/A"

        if isinstance(value, (float, np.floating)):
            if float(value).is_integer():
                return str(int(value))

            return f"{float(value):,.2f}"

        if isinstance(value, (int, np.integer)):
            return f"{int(value):,}"

        return str(value)

    # Helper for creating readable, page-splitting tables.
    def add_table(dataframe):

        if dataframe is None or dataframe.empty:
            story.append(
                Paragraph("No data available.", body_style)
            )
            return

        display_df = dataframe.copy()

        if not isinstance(display_df.index, pd.RangeIndex):
            display_df.insert(
                0,
                "Column",
                display_df.index.astype(str)
            )

        available_width = (
            document.width
        )

        column_count = len(display_df.columns)

        # Divide the available page width among columns.
        column_width = available_width / column_count

        table_data = []

        # Header row
        header = [
            Paragraph(
                escape(str(col)),
                header_cell_style
            )
            for col in display_df.columns
        ]

        table_data.append(header)

        # Data rows
        for _, row in display_df.iterrows():

            table_row = []

            for value in row:

                formatted_value = escape(
                    format_value(value)
                )

                table_row.append(
                    Paragraph(
                        formatted_value,
                        table_cell_style
                    )
                )

            table_data.append(table_row)

        pdf_table = LongTable(
            table_data,
            colWidths=[column_width] * column_count,
            repeatRows=1,
            hAlign="LEFT",
            splitByRow=1
        )

        pdf_table.setStyle(TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#243B64")
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.35,
                colors.HexColor("#D0D7E2")
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F2F5FA")
                ]
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            )
        ]))

        story.append(pdf_table)
        story.append(Spacer(1, 10))

    # Report title
    story.append(
        Paragraph("DataMind AI", title_style)
    )

    story.append(
        Paragraph(
            "Executive Data Analysis Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 12))

    # 1. Dataset overview
    story.append(
        Paragraph("1. Dataset Overview", heading_style)
    )

    add_table(
        pd.DataFrame([report_data["overview"]])
    )

    # 2. Executive findings
    story.append(
        Paragraph("2. Executive Findings", heading_style)
    )

    for finding in findings:

        story.append(
            Paragraph(
                f"&bull; {escape(str(finding))}",
                body_style
            )
        )

    # 3. Data quality
    story.append(
        Paragraph("3. Data Quality Analysis", heading_style)
    )

    story.append(
        Paragraph("Missing Values", subheading_style)
    )

    add_table(report_data["missing_values"])

    story.append(
        Paragraph("Column Information", subheading_style)
    )

    add_table(report_data["column_info"])

    # 4. Exploratory data analysis
    story.append(
        Paragraph(
            "4. Exploratory Data Analysis",
            heading_style
        )
    )

    story.append(
        Paragraph("Numerical Summary", subheading_style)
    )

    add_table(report_data["numeric_summary"])

    story.append(
        Paragraph("Categorical Summary", subheading_style)
    )

    add_table(report_data["categorical_summary"])

    # Start the correlation matrix on a fresh page so its heading and
    # table are not stranded at the bottom of the preceding page.
    story.append(PageBreak())

    story.append(
        Paragraph("Correlation Matrix", subheading_style)
    )

    add_table(report_data["correlation_matrix"])

    # 5. Outlier analysis
    story.append(
        Paragraph("5. Outlier Analysis", heading_style)
    )

    add_table(report_data["outlier_summary"])

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Generated automatically by DataMind AI.",
            body_style
        )
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
