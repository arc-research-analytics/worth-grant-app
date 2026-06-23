# Reporting App for WORTH Grant

A Streamlit web application that automates participant data collection and PII anonymization for the Wells Fargo WORTH Grant, maintained by the Atlanta Regional Commission. Access the live app [here](https://data-cleaning-app-arc.streamlit.app/).

## What It Does

The app guides participating organizations through a three-step reporting workflow:

1. **Instructions** — Overview of the reporting process and what to expect.
2. **Download Template** — User selects a service category from a dropdown and downloads a pre-formatted Excel template. The template is generated on the fly with 50 pre-populated rows (Column A filled with the service name), correct column headers for that service type, and embedded dropdown validation for applicable fields.
3. **Upload & Anonymize** — User uploads their completed template. The app validates that all required columns are present, detects the service type from the data, generates a unique ID for each participant row, and packages two output files into a timestamped ZIP for download:
   - A **KEEP** file — full data including PII, for the organization's internal records.
   - A **SEND** file — PII removed, for submission to the grant program.

## Output Columns

All templates share a base set of columns. A few fields vary by service type:

| Column | KEEP | SEND | Notes |
|---|---|---|---|
| Service | ✓ | ✓ | Auto-populated in template |
| Submitting Organization | ✓ | ✓ | |
| Service Completion Date | ✓ | ✓ | Normalized to MM/DD/YYYY |
| Counseling Service Rendered | ✓ | ✓ | Housing Counseling only; dropdown-validated |
| Unique ID | ✓ | ✓ | Generated from Name + DOB; see below |
| Name | ✓ | — | PII; stripped from SEND |
| Date of Birth | ✓ | — | PII; stripped from SEND |
| Street Address | ✓ | — | PII; stripped from SEND |
| Unit (if applicable) | ✓ | — | PII; stripped from SEND |
| County | ✓ | ✓ | |
| ZIP | ✓ | ✓ | |
| Race | ✓ | ✓ | |
| Ethnicity | ✓ | ✓ | |
| Primary Language | ✓ | ✓ | |
| Gender | ✓ | ✓ | |
| HH Income | ✓ | ✓ | |
| HH Size | ✓ | ✓ | |
| Existing Homeowner (Y/N) | ✓ | ✓ | All types except Education |
| First-Generation Homeowner (Y/N) | ✓ | ✓ | All types except Education |
| 1st Time Home Buyer (Y/N) | ✓ | ✓ | Education only |
| Has Sold? | ✓ | ✓ | New Units Produced only; dropdown-validated (TRUE/FALSE) |

## Unique ID Algorithm

Each participant receives a non-reversible unique ID to enable longitudinal tracking without retaining PII. The ID is constructed as:

```
{name_part}-{dob_part}
```

- **name_part** — Name with spaces removed, lowercased; every 3rd character starting from index 1; truncated to 4 characters, left-padded with `x` if shorter.
- **dob_part** — Number of days between DOB and a fixed reference date (1920-01-02); every 2nd character of that number as a string.

All IDs in the output are right-padded with `0` to a uniform length matching the longest ID in the batch.

## Tech Stack

| Technology | Role |
|---|---|
| Streamlit 1.40.2 | Web app framework and UI |
| Pandas 2.2.2 | DataFrame parsing, transformation, and output |
| openpyxl 3.1.2 | Reading `.xlsx` input files |
| XlsxWriter 3.1.9 | Writing output `.xlsx` files with auto-fit columns |
| pytz 2024.2 | Eastern timezone formatting for ZIP timestamps |

## Running Locally

```bash
pip install -r requirements.txt
streamlit run main.py
```

The app is deployed on Streamlit Community Cloud.

## Important Constraint

The column schemas defined in the template generator (`views/2_download_template.py`) and the column validator in the upload page (`views/3_upload_template.py`) must stay in sync. If a column is added, removed, or renamed in one, it must be updated in both.
