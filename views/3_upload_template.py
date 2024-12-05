import streamlit as st
import pandas as pd
import io
import zipfile
from datetime import datetime
from pytz import timezone

# set page configuration
st.set_page_config(
    layout='centered',
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(
    """
    <style>
        [data-testid="stFileUploaderDropzone"] {
            background-color: #FFFFF6;
            border-radius: 15px;
            border: 1px solid #1F2041;
            padding: 15px; /* Optional: Add some padding */
        }
        div[data-testid="stFileUploaderDropzoneInstructions"]>div>span {
            visibility: hidden;
        }
        div[data-testid="stFileUploaderDropzoneInstructions"]>div>span::before {
            content: "Drag & drop completed Excel template for cleaning.";
            visibility: visible;
        }
        div[data-testid="stFileUploaderDropzoneInstructions"]>div>small {
            visibility: hidden;
        }
        div[data-testid="stFileUploaderDropzoneInstructions"]>div>small::before {
            content: "Limit one file per upload.";
            visibility: visible;
        }
        .stDownloadButton, div.stButton {text-align:center}
    </style>
    """,
    unsafe_allow_html=True
)

# top of page spacing
st.write("")

# title text
st.markdown(f'''
    <p style="font-size: 40px; font-weight: 900; text-align: center; margin-bottom: 30px;">
        Upload Your Template
    </p>
''', unsafe_allow_html=True)

# instructional text
st.markdown(f'''
    <p style="font-size: 23px; font-weight: 200; text-align: left;">
        Once you have copied your data to the template downloaded from Page 2, upload it below. Note that your uploaded data must contain all the fields originally included from the template you downloaded (and no new columns can be included). This app will anonymize your data and provide a unique ID field for each row of data.
    </p>
''', unsafe_allow_html=True)


# Function to scrub data
def scrub_data(df, original_filename):

    # Extract final 4 digits from 'Service Date'
    service_date_digits = df['Service Date'].astype(str).str[-4:]

    # Concatenate 'Street Address' and 'Unit (if applicable)'
    # - Replace NaN or empty 'Unit (if applicable)' values with 'Na'
    combined_address = (
        df['Street Address'].astype(str) +
        df['Unit (if applicable)'].fillna('Na').replace('', 'Na')
    )

    # Process the combined address:
    # - Remove spaces
    # - Convert to lowercase
    # - Limit to the first 20 characters and take every 3rd character
    processed_combined_address = (
        combined_address
        .str.replace(' ', '', regex=True)
        .str.lower()
        .str[:20]
        .apply(lambda x: x[::3])
    )

    # Create 'Unique ID'
    df['Unique ID'] = processed_combined_address + service_date_digits

    # Zero-pad all values in 'Unique ID' to the same length as the max value
    max_length = df['Unique ID'].str.len().max()
    df['Unique ID'] = df['Unique ID'].apply(lambda x: x.ljust(max_length, '0'))

    # Truncate 'Service' and 'Unique ID' columns based on the number of non-null 'Street Address' values
    valid_count = df['Street Address'].notna().sum()

    # Truncate the 'Service' and 'Unique ID' columns
    df.loc[valid_count:, ['Service', 'Unique ID']] = None

    # Properly format the dates
    df['Service Date'] = pd.to_datetime(
        df['Service Date']).dt.strftime('%m/%d/%Y')

    # Create two versions of the DataFrame
    keep_df = df.copy()
    send_df = df.drop(columns=['Street Address', 'Unit (if applicable)'])

    # rearrage columns
    keep_df = keep_df[[
        "Service",
        "Service Date",
        "Unique ID",
        "Street Address",
        "Unit (if applicable)",
        "County",
        "ZIP",
        "Race",
        "Ethnicity",
        "Gender",
        "Age",
        "HH Income"
    ]]
    send_df = send_df[[
        "Service",
        "Service Date",
        "Unique ID",
        "County",
        "ZIP",
        "Race",
        "Ethnicity",
        "Gender",
        "Age",
        "HH Income"
    ]]

    # Save both DataFrames to Excel files in memory buffers
    keep_buffer = io.BytesIO()
    keep_filename = f"{original_filename.split('.')[0]}_clean_KEEP.xlsx"
    with pd.ExcelWriter(keep_buffer, engine='xlsxwriter') as writer:
        keep_df.to_excel(writer, index=False, sheet_name='Data')
        writer.sheets['Data'].autofit()
    keep_buffer.seek(0)

    send_buffer = io.BytesIO()
    send_filename = f"{original_filename.split('.')[0]}_clean_SEND.xlsx"
    with pd.ExcelWriter(send_buffer, engine='xlsxwriter') as writer:
        send_df.to_excel(writer, index=False, sheet_name='Data')
        writer.sheets['Data'].autofit()
    send_buffer.seek(0)

    return keep_buffer, keep_filename, send_buffer, send_filename


# Streamlit App
def main():

    # Expected column names
    expected_columns = [
        "Service",
        "Service Date",
        "Street Address",
        "Unit (if applicable)",
        "County",
        "ZIP",
        "Race",
        "Ethnicity",
        "Gender",
        "Age",
        "HH Income"
    ]

    # File upload widget
    uploaded_file = st.file_uploader(
        label="Choose completed reporting template",
        label_visibility='collapsed',
        accept_multiple_files=False,
        help="Upload the completed Excel template you downloaded from Page 2 of this web application."
    )

    if uploaded_file:
        # Read uploaded file into DataFrame
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            st.error(
                "File format not supported! Please upload a CSV or Excel file.")
            st.stop()

        # Validate column names
        uploaded_columns = list(df.columns)
        missing_columns = [
            col for col in expected_columns if col not in uploaded_columns]
        extra_columns = [
            col for col in uploaded_columns if col not in expected_columns]

        if missing_columns or extra_columns:
            if missing_columns:
                st.error(
                    f"Uploaded file missing the following column(s): {', '.join(missing_columns)}. Please modify your source data and upload again!"
                )
            if extra_columns:
                st.error(
                    f"Uploaded file contains the following extra column(s): {', '.join(extra_columns)}")
            st.stop()

        # Button to scrub and download data
        tz = timezone("America/New_York")
        timestamp = datetime.now(tz).strftime("%m-%d-%Y_%I.%M%p")
        zip_file_name = f"{uploaded_file.name.split('.')[0]}_cleaned_{timestamp}.zip"

        # Scrub data and package into ZIP
        def scrub_and_package():
            keep_buffer, keep_filename, send_buffer, send_filename = scrub_data(
                df, uploaded_file.name)

            # Create a ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                zip_file.writestr(keep_filename, keep_buffer.getvalue())
                zip_file.writestr(send_filename, send_buffer.getvalue())
            zip_buffer.seek(0)
            return zip_buffer

        # Provide the ZIP download button
        st.download_button(
            label="Scrub & Download",
            data=scrub_and_package(),
            file_name=zip_file_name,
            mime="application/zip",
        )


main()