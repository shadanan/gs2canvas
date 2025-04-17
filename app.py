import io

import pandas as pd
import streamlit as st

import gs2canvas

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
sdf = pd.read_csv(buf, skiprows=[1])
for col in gs2canvas.STUDENT_DB_COLUMNS:
    if col not in sdf.columns:
        st.error(f"`{col}` is missing in `{student_db_file.name}`")
        st.stop()
sdf = sdf[gs2canvas.STUDENT_DB_COLUMNS]
st.write(sdf)

gs_responses_file = st.file_uploader(
    "Google Sheet Responses",
    type="csv",
    help="A csv file containing the scores (Score) of each student (Email Address), typically exported from Google Sheets.",
)

if gs_responses_file is None:
    st.stop()

buf = io.StringIO(gs_responses_file.getvalue().decode("utf-8"))
rdf = pd.read_csv(buf)
for col in gs2canvas.GS_RESPONSE_COLUMNS:
    if col not in rdf.columns:
        st.error(f"`{col}` is missing in `{gs_responses_file.name}`")
        st.stop()
rdf = rdf[gs2canvas.GS_RESPONSE_COLUMNS]
st.write(rdf)

mdf = rdf.merge(sdf, how="left", left_on="Email Address", right_on="SIS Login ID")
mdf = mdf[mdf["SIS Login ID"].isnull()][gs2canvas.GS_RESPONSE_COLUMNS]
if len(mdf) > 0:
    st.warning("Some students failed to join:")
    st.write(mdf)

name = st.text_input("Test / Assignment Name")
if name != "":
    cdf = gs2canvas.convert(sdf, rdf, name)
    st.write("## Canvas Formatted Data")
    st.write(cdf)
    result = io.StringIO()
    cdf.to_csv(result, index=False)
    result.seek(0)
    st.download_button(
        "Download as CSV",
        data=result.read(),
        file_name=f"canvas-{gs2canvas.to_kebab_case(name)}-import.csv",
    )
