import pandas as pd
import streamlit as st
def load_csv(uploaded_file):
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        if df.empty:
            raise ValueError("The uploaded CSV is empty")
        if len(df.columns)==0:
            raise ValueError("No columns found in the CSV")
        df.columns = df.columns.astype(str).str.strip()
        return df
    except pd.errors.EmptyDataError:
        st.error("The uploaded file contains no data")
    except pd.errors.ParserError:
        st.error("Unable to parse the CSV file")
    except UnicodeDecodeError:
        st.error("Encoding issues. Please upload a UTF-8 CSV File")
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        st.error(f"Unexpected Error : {error}")
    return None 