import streamlit as st
import pandas as pd
import io

# set page configuration
st.set_page_config(
    layout='centered',
    initial_sidebar_state="expanded"
)

# custom CSS
hide_default_format = """
    <style>
        [data-testid="stMainBlockContainer"] {
            padding-top: 100px;
        }
        [data-testid="stBaseButton-secondary"] {
            background-color: #FFFFF6;
        }
        div[data-baseweb="select"] > div {
            background-color: #FFFFF6;
        }
        .stDownloadButton, div.stButton {text-align:center}
    </style>
"""

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)

# title text
st.markdown(f'''
    <p style="font-size: 40px; font-weight: 900; text-align: center; margin-bottom: 30px;">
        Download Your Template
    </p>
''', unsafe_allow_html=True)

# instructional text
st.markdown(f'''
    <p style="font-size: 23px; font-weight: 200; text-align: left;">
        Please select a service category to download the corresponding template to use for your reporting. The template comes with Column A populated down to 50 rows. If you have fewer than 50 rows of data to report, you can delete the extra rows.
    </p>
''', unsafe_allow_html=True)

# dropdown menu
service_rendered = st.selectbox(
    placeholder="Select a service category",
    index=None,
    label="hi",
    label_visibility='hidden',
    options=[
        "New Units Produced",
        "Housing Counseling",
        "Down Payment Assistance",
        "Home Rehabilitation",
        "Legacy Resident Tax Relief",
        "Heirs Property Resolution",
        "Foreclosure Prevention",
        "Education",
        "CDFI Activity",
    ],
)
st.write("")
st.write("")
st.write("")

# define the columns & widths in the spreadsheet
columns_to_keep = {
    "Service": 20,
    "Submitting Organization": 25,
    "Service Completion Date": 20,
    "Name": 20,
    "Date of Birth": 15,
    "Street Address": 35,
    "Unit (if applicable)": 20,
    "County": 20,
    "ZIP": 8,
    "Race": 10,
    "Ethnicity": 10,
    "Gender": 10,
    "HH Income": 15
}

# auto-fill the first N rows
rows_in_spreadsheet = 50

data = {"Service": [service_rendered] * rows_in_spreadsheet}
for col in columns_to_keep.keys():
    if col != "Service":  # Add other columns as empty
        data[col] = ["" for _ in range(rows_in_spreadsheet)]
df = pd.DataFrame(data)

buffer = io.BytesIO()

# Write the DataFrame to the buffer using ExcelWriter
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    # Access the workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Set column widths
    for col_num, (col_name, width) in enumerate(columns_to_keep.items()):
        worksheet.set_column(col_num, col_num, width)

# Download button
if service_rendered:
    service_rendered_no_spaces = service_rendered.replace(" ", "")
    file_name = f"{service_rendered_no_spaces}_template.xlsx"
    st.download_button(
        label=f"Download Template for {service_rendered}",
        data=buffer,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
