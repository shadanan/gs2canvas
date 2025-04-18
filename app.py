import io

import pandas as pd
import streamlit as st

import gs2canvas


@st.cache_data
def convert_for_download(df: pd.DataFrame):
    return df.to_csv().encode()


st.write("""
# gs2canvas

This Streamlit converts Google Sheet form responses to a format compatible with Canvas's import tool.
""")

student_db_file = st.file_uploader(
    "Canvas Student DB",
    type="csv",
    help="A csv file containing a map from student email (SIS Login ID) to student name (Student), typically exported from Canvas.",
)

if student_db_file is None:
    st.stop()

buf = io.StringIO(student_db_file.getvalue().decode("utf-8"))
sdf = gs2canvas.load_student_db(buf)
st.dataframe(sdf)

gs_responses_file = st.file_uploader(
    "Google Sheet Responses",
    type="csv",
    help="A csv file containing the scores (Score) of each student (Email Address), typically exported from Google Sheets.",
)

if gs_responses_file is None:
    st.stop()

buf = io.StringIO(gs_responses_file.getvalue().decode("utf-8"))
rdf = gs2canvas.load_gs_responses(buf)
st.dataframe(rdf)

mdf = rdf.merge(sdf, how="left", left_on="Email Address", right_on="SIS Login ID")
mdf = mdf[mdf["SIS Login ID"].isnull()][gs2canvas.GS_RESPONSE_COLUMNS]
if len(mdf) > 0:
    st.warning("Some students failed to join:")
    st.dataframe(mdf)

name = st.text_input("Test / Assignment Name")
if name != "":
    cdf = gs2canvas.convert(sdf, rdf, name)
    st.write("## Canvas Formatted Data")
    st.dataframe(cdf)
    st.download_button(
        "Download as CSV",
        data=convert_for_download(cdf),
        file_name=f"canvas-{gs2canvas.to_kebab_case(name)}-import.csv",
    )
