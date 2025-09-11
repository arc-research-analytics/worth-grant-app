import streamlit as st

# set page configurations
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# heading text
st.markdown(f'''
    <p style="font-size: 40px; font-weight: 900; text-align: center; margin-bottom: 50px;">
        Data Validation & Reporting App
    </p>
''', unsafe_allow_html=True)

# paragraph text
st.markdown(f'''
    <p style="font-size: 23px; font-weight: 200; text-align: left;">
        This web application will aid in the reporting process for the Wells Fargo WORTH Grant. To get started, navigate to Page 2 in the sidebar panel to download your proper reporting template. <i>Please use this Excel template to report your data, as it will contain the exact fields you need!</i><br/><br/>
        Once you have filled out your template, return to Page 3 of this web application to upload your data. The application will anonymize your template data and provide two files for download: one with all fields plus a unique user ID column and one with address fields removed but with the unique ID field retained. <br/><br/>
        Keep the former file for your records, but return the latter file to Will Wright at <a href="mailto:wwright@atlantaregional.org?subject=Question%20re%3A%20validator%20app">wwright@atlantaregional.org</a>.
    </p>
''', unsafe_allow_html=True)

# custom CSS
hide_default_format = """
    <style>
        [data-testid="stMainBlockContainer"] {
            padding-top: 100px;
        }
    </style>
"""

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
