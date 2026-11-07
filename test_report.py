import pandas as pd
from modules.report_generator import generate_pdf_report

df = pd.read_csv("sample_data/titanic.csv")

pdf_content = generate_pdf_report(df)

with open("test_report.pdf", "wb") as file:
    file.write(pdf_content)

print("PDF report generated successfully!")
