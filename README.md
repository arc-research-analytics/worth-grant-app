# Reporting App for WORTH Grant

A Streamlit app that streamlines data collection and submission for the Wells Fargo WORTH Grant, maintained by the Atlanta Regional Commission.

## What It Does

The app guides participating organizations through a three-step workflow:

1. **Instructions** — Overview of the reporting process.
2. **Download Template** — Select your service category and download a pre-formatted Excel template with built-in data validation dropdowns.
3. **Upload Template** — Upload your completed template. The app anonymizes participant PII, then packages two files into a ZIP for download:
   - A **KEEP** file (full data for the organization's records)
   - A **SEND** file (PII-removed version for grant submission)

Supported service categories: New Units Produced, Housing Counseling, Down Payment Assistance, Home Rehabilitation, Legacy Resident Tax Relief, Heirs Property Resolution, Education, and CDFI Activity.

## Setup

```bash
pip install -r requirements.txt
streamlit run main.py
```

## How Anonymization Works

Each participant receives a non-reversible unique ID derived from their name and date of birth. The SEND file strips Name, Date of Birth, and address fields while preserving demographic data (Race, Ethnicity, Primary Language, Gender).

## Deployment

The app is hosted on Streamlit Community Cloud. A GitHub Actions workflow ([.github/workflows/caffeine.yml](.github/workflows/caffeine.yml)) updates a timestamp file six times daily to prevent the instance from going to sleep.
