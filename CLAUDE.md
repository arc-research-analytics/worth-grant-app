# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
conda activate research
streamlit run main.py
```

Hot reload is enabled (`runOnSave = true`), so changes take effect automatically. The app runs at `http://localhost:8501` by default.

## Installing Dependencies

```bash
conda activate research
pip install -r requirements.txt
```

## Architecture

This is a three-page Streamlit app for the **Wells Fargo WORTH Grant** data submission workflow, maintained by Atlanta Regional Commission. The workflow is linear: Instructions → Download Template → Upload & Anonymize.

### Page Structure

- [main.py](main.py) — Entry point. Sets up `st.navigation()` with three pages and injects CSS to hide default Streamlit chrome.
- [views/1_instructions.py](views/1_instructions.py) — Static landing page explaining the workflow.
- [views/2_download_template.py](views/2_download_template.py) — Generates downloadable Excel templates dynamically based on a selected service category. Supports 8 service types, each with a different column schema. Uses `openpyxl` to embed dropdown data validation in the generated file.
- [views/3_upload_template.py](views/3_upload_template.py) — The core logic page. Accepts uploaded Excel files, validates columns against expected schema, runs `scrub_data()` to anonymize PII, and packages two output files into a timestamped ZIP: a "KEEP" file (full data for the org) and a "SEND" file (PII-removed for grant submission).

### Key Logic: `scrub_data()` in [views/3_upload_template.py](views/3_upload_template.py)

- Generates a non-reversible unique ID from the participant's name (every 3rd character) + date of birth (every 2nd digit of a day offset). This ID allows longitudinal tracking without retaining PII.
- Strips Name, DOB, Street Address, and Unit from the "SEND" file while preserving demographic fields (Race, Ethnicity, Language, Gender).
- Dates are normalized to MM/DD/YYYY; missing/unparseable dates are handled gracefully.
- Output ZIP is named with an Eastern-timezone timestamp via `pytz`.

### Service Type Column Schemas

The 8 service categories share a base column set but diverge in a few fields. Housing Counseling adds a `Housing Counseling Type` column; Education uses different activity columns; CDFI Activity has its own schema. The template generator in page 2 and the validator in page 3 must stay in sync — if you update column definitions in one, update both.

### GitHub Actions: Keep-Alive

[.github/workflows/caffeine.yml](.github/workflows/caffeine.yml) runs 6× daily to update [Assets/timestamp.txt](Assets/timestamp.txt), preventing the hosted Streamlit instance from going to sleep.

## Theme

Defined in [.streamlit/config.toml](.streamlit/config.toml):
- Primary: `#1F2041` (navy)
- Background: `#FFFFF6` (cream)
- Secondary/accent: `#E55934` (orange)
