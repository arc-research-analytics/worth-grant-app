import streamlit as st

# - - - PAGE SETUP - - -
home = st.Page(
    page='views/1_instructions.py',
    title='1 - Instructions',
    icon=':material/home:',
    default=True
)

download_template = st.Page(
    page='views/2_download_template.py',
    title='2 - Download Template',
    icon=':material/download:'
)

upload_template = st.Page(
    page='views/3_upload_template.py',
    title='3 - Upload Template',
    icon=':material/upload:'
)


# - - - NAVIGATION SETUP - - -
pg = st.navigation(
    pages=[
        home,
        download_template,
        upload_template,
    ])


# - - - RUN NAVIGATION - - -
pg.run()

# the custom CSS lives here:
hide_default_format = """
    <style>
        .reportview-container .main footer {visibility: hidden;}    
        #MainMenu, header, footer {visibility: hidden;}
        div.stActionButton{visibility: hidden;}
        [class="stAppDeployButton"] {
            display: none;
        }
    </style>
"""

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
