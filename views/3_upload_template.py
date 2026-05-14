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
        Once you have copied your data to the template downloaded from Page 2, upload it below. <i>Note that your uploaded data must contain all the fields originally included from the template you downloaded</i>. This app will anonymize your data and provide a unique ID field for each row of data.
    </p>
''', unsafe_allow_html=True)


# Function to scrub data
def scrub_data(df, original_filename, service_type):
    # Initialize warnings list
    warnings = []
    
    # Validate date columns before processing
    try:
        # Convert 'Date of Birth' to datetime with error handling - this is non-critical
        df['Date of Birth'] = pd.to_datetime(df['Date of Birth'], errors='coerce')
        # # Check if any dates couldn't be parsed
        # if df['Date of Birth'].isna().any():
        #     invalid_dob_rows = df[df['Date of Birth'].isna()].index.tolist()
        #     warnings.append(f"Warning: Invalid date format found in 'Date of Birth' column. While not essential, this field is used to generate a unique ID for each record. This unique ID can still be generatged, but it will not be based on accurate, record-level information for that individual. Proceed with caution!")
            
        #     # For missing Date of Birth values, set a default date to allow processing to continue
        #     df.loc[df['Date of Birth'].isna(), 'Date of Birth'] = pd.Timestamp('1900-01-01')

        # clean up the 'Service Completion Date' column
        df['Service Completion Date'] = df['Service Completion Date'].astype(str).str.strip()
        df['Service Completion Date'] = df['Service Completion Date'].replace(['', ' ', 'nan', 'None', 'N/A'], pd.NaT)

        # Convert 'Service Completion Date' to datetime with error handling - this is critical
        df['Service Completion Date'] = pd.to_datetime(df['Service Completion Date'], errors='coerce')
        # if df['Service Completion Date'].isna().any():
        #     invalid_scd_rows = df[df['Service Completion Date'].isna()].index.tolist()
        #     error_msg = f"Invalid date format found in 'Service Completion Date' column. Please check your data and upload again with this column filled in with proper date formatting."
        #     return None, None, None, None, error_msg, warnings
    
        reference_date = pd.Timestamp('1920-01-02')
        days_old = ((df['Date of Birth'] -
                    reference_date).dt.days).astype(str).apply(lambda x: x[::2])
    
        name_format = df['Name'].astype(str).str.replace(
            ' ', '', regex=True).str.lower().apply(lambda x: x[1:][::3]).str[:4].str.ljust(4, 'x')
    
        df['Unique ID'] = name_format.astype(str) + "-" + days_old.astype(str)
    
        # Zero-pad all values in 'Unique ID' to the same length as the max value
        max_length = df['Unique ID'].str.len().max()
        df['Unique ID'] = df['Unique ID'].apply(lambda x: x.ljust(max_length, '0'))
    
        # Calculate number of non-null 'Name' values
        valid_count = df['Name'].notna().sum()
    
        # Truncate the 'Service' and 'Unique ID' columns
        df.loc[valid_count:, ['Service', 'Unique ID']] = None
    
        # Properly format the dates
        df['Service Completion Date'] = df['Service Completion Date'].dt.strftime('%m/%d/%Y')
        df['Date of Birth'] = df['Date of Birth'].dt.strftime('%m/%d/%Y')
    
        # Create two versions of the DataFrame
        keep_df = df.copy()
        send_df = df.drop(columns=['Name', 'Date of Birth',
                        'Street Address', 'Unit (if applicable)'])

        # Build column order dynamically based on service type
        keep_columns = [
            "Service",
            "Submitting Organization",
            "Service Completion Date",
        ]

        # Add service-specific column for Housing Counseling
        if service_type == "Housing Counseling":
            keep_columns.append("Counseling Service Rendered")

        keep_columns.extend([
            "Unique ID",
            "Name",
            "Date of Birth",
            "Street Address",
            "Unit (if applicable)",
            "County",
            "ZIP",
        ])

        for col in ["Race", "Ethnicity", "Primary Language", "Gender"]:
            if col in df.columns:
                keep_columns.append(col)

        keep_columns.extend([
            "HH Income",
            "HH Size",
        ])

        # Add ending columns based on template type
        if service_type == "Education":
            keep_columns.append("1st Time Home Buyer (Y/N)")
        else:
            keep_columns.extend([
                "Existing Homeowner (Y/N)",
                "First-Generation Homeowner (Y/N)"
            ])

        if service_type == "New Units Produced":
            keep_columns.append("Has Sold?")

        # Build send columns (excluding PII)
        send_columns = [
            "Service",
            "Submitting Organization",
            "Service Completion Date",
        ]

        if service_type == "Housing Counseling":
            send_columns.append("Counseling Service Rendered")

        send_columns.extend([
            "Unique ID",
            "County",
            "ZIP",
        ])

        for col in ["Race", "Ethnicity", "Primary Language", "Gender"]:
            if col in df.columns:
                send_columns.append(col)

        send_columns.extend([
            "HH Income",
            "HH Size",
        ])

        if service_type == "Education":
            send_columns.append("1st Time Home Buyer (Y/N)")
        else:
            send_columns.extend([
                "Existing Homeowner (Y/N)",
                "First-Generation Homeowner (Y/N)"
            ])

        if service_type == "New Units Produced":
            send_columns.append("Has Sold?")

        # Append any extra columns (not in the standard template) at the end of both outputs
        extra_cols = [col for col in df.columns if col not in keep_columns]
        keep_columns.extend(extra_cols)
        send_columns.extend(extra_cols)

        # Rearrange columns
        keep_df = keep_df[keep_columns]
        send_df = send_df[send_columns]
    
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
    
        return keep_buffer, keep_filename, send_buffer, send_filename, None, warnings
    
    except Exception as e:
        return None, None, None, None, f"An error occurred during data processing: {str(e)}", warnings


# Streamlit App
def main():

    # Base columns shared by all templates
    base_columns = [
        "Service",
        "Submitting Organization",
        "Service Completion Date",
    ]

    # Common columns after service-specific ones
    common_columns = [
        "Name",
        "Date of Birth",
        "Street Address",
        "Unit (if applicable)",
        "County",
        "ZIP",
        "HH Income",
        "HH Size",
    ]

    # Default ending columns for most templates
    default_ending_columns = [
        "Existing Homeowner (Y/N)",
        "First-Generation Homeowner (Y/N)"
    ]

    # Function to build expected columns based on service type
    def get_expected_columns(service_type):
        columns = base_columns.copy()

        # Add service-specific column for Housing Counseling
        if service_type == "Housing Counseling":
            columns.append("Counseling Service Rendered")

        # Add common columns
        columns.extend(common_columns)

        # Add ending columns based on template type
        if service_type == "Education":
            columns.append("1st Time Home Buyer (Y/N)")
        else:
            columns.extend(default_ending_columns)

        if service_type == "New Units Produced":
            columns.append("Has Sold?")

        return columns

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

        # Detect service type from uploaded data
        service_type = None
        if "Service" in df.columns and len(df) > 0:
            service_type = df["Service"].dropna().iloc[0] if not df["Service"].dropna().empty else None

        # Get expected columns based on service type
        expected_columns = get_expected_columns(service_type)

        # Validate column names
        uploaded_columns = list(df.columns)
        missing_columns = [
            col for col in expected_columns if col not in uploaded_columns]
        extra_columns = [
            col for col in uploaded_columns if col not in expected_columns]

        if missing_columns:
            st.error(
                f"Uploaded file missing the following column(s): {', '.join(missing_columns)}. Please modify your source data and upload again!"
            )
            st.stop()


        # Button to scrub and download data
        tz = timezone("America/New_York")
        timestamp = datetime.now(tz).strftime("%m-%d-%Y_%I.%M%p")
        zip_file_name = f"{uploaded_file.name.split('.')[0]}_cleaned_{timestamp}.zip"

        # Scrub data and package into ZIP
        def scrub_and_package():
            keep_buffer, keep_filename, send_buffer, send_filename, error_msg, warnings = scrub_data(
                df, uploaded_file.name, service_type)

            # Display any warnings first
            for warning in warnings:
                st.warning(warning)

            # If there's an error, display it and return None
            if error_msg:
                st.error(error_msg)
                return None

            # Create a ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                zip_file.writestr(keep_filename, keep_buffer.getvalue())
                zip_file.writestr(send_filename, send_buffer.getvalue())
            zip_buffer.seek(0)
            return zip_buffer

        # Provide the ZIP download button
        zip_data = scrub_and_package()
        if zip_data is not None:
            st.download_button(
                label="Scrub & Download",
                data=zip_data,
                file_name=zip_file_name,
                mime="application/zip",
            )


main()
