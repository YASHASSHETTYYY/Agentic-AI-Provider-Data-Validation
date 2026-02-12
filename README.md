# Agentic AI Provider Data Validation

A lightweight demo application that simulates how an **agentic AI workflow** can validate and enrich healthcare provider directory data.

The project includes:
- A **Streamlit frontend** for uploading CSV files, running simulated validation, and reviewing outcomes.
- A minimal **FastAPI backend service** health endpoint.
- Sample test data for trying the dashboard end-to-end.

---

## Overview

Healthcare payer operations teams often spend significant manual effort cleaning and validating provider records. This repository demonstrates a UI-driven workflow where AI agents:

1. Ingest provider directory records from a CSV upload.
2. Simulate multi-source validation (e.g., NPI Registry, Google Maps, provider website).
3. Produce confidence scores and risk levels.
4. Surface data changes and reasoning for review.
5. Export an updated provider directory CSV.

> **Note:** Current validation logic is intentionally simulated (randomized) for prototype/demo purposes.

---

## Repository Structure

```text
.
├── app/
│   ├── main.py                 # Streamlit application
│   └── backend/
│       └── main.py             # FastAPI backend (health endpoint)
├── provider_directory_test_data.csv
├── PROVIDER_PROFILES.md        # Product/UX notes and profile examples
├── requirements.txt
└── README.md
```

---

## Features

### Streamlit Dashboard
- CSV uploader for provider directory files.
- “Start Validation” trigger for simulated AI validation.
- Live activity log:
  - High-level progress updates.
  - Optional detailed per-provider logs.
- Executive summary KPIs:
  - Total providers processed.
  - Providers flagged for review.
  - Average confidence score.
  - Estimated manual effort saved.
- Data quality metrics:
  - Phone numbers corrected.
  - Addresses updated.
  - Missing fields filled.
- Risk-prioritized provider list (High/Medium attention first).
- Per-provider expandable details:
  - Before/after field comparison.
  - Validation reasoning.
  - Sources used.
  - Manual review action buttons.
- Download options:
  - Updated CSV.
  - Mock PDF report.

### Backend Service (FastAPI)
- Minimal service scaffold with root endpoint:
  - `GET /` → returns status message indicating backend availability.

---

## Data Model (Input CSV)

A sample input file is provided: `provider_directory_test_data.csv`.

Expected columns (from the sample file):

- `provider_id`
- `first_name`
- `last_name`
- `specialty`
- `phone`
- `email`
- `address`
- `city`
- `state`
- `zip`
- `npi_number`
- `license_number`

The app is resilient to schema variation, but these fields best match the supplied sample and dashboard behavior.

---

## How Validation Is Simulated

For each row in the uploaded CSV, the Streamlit app:

1. Iterates each column value.
2. Randomly assigns one of three outcomes:
   - **verified** (most common)
   - **updated** (value modified with “(updated)”, confidence penalty)
   - **invalid** (value replaced with `N/A`, larger confidence penalty)
3. Randomly assigns a data source for each check.
4. Aggregates outcomes to compute:
   - Provider confidence score.
   - Provider risk level: `Low`, `Medium`, or `High`.
   - Primary issue for non-low risk records.
5. Stores detailed artifacts in session state for rendering and download.

Because randomness is used, repeated runs on the same input can produce different outputs.

---

## Prerequisites

- Python 3.10+ recommended.
- `pip` for package installation.

---

## Installation

```bash
pip install -r requirements.txt
```

Dependencies currently listed:
- streamlit
- pandas
- fastapi
- uvicorn
- plotly

---

## Running the Application

### 1) Start the Streamlit UI

```bash
streamlit run app/main.py
```

Then open the local URL shown in your terminal (typically `http://localhost:8501`).

### 2) (Optional) Start the FastAPI backend

```bash
uvicorn app.backend.main:app --reload --port 8000
```

Check health/status:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{"message":"Agentic AI Backend is running."}
```

---

## Typical Usage Flow

1. Launch Streamlit.
2. Upload `provider_directory_test_data.csv` (or your own CSV).
3. Click **Start Validation**.
4. Review:
   - Executive summary metrics.
   - Immediate-attention providers.
   - Per-provider details in expanders.
5. Download updated directory CSV.

---

## Known Limitations

- Validation is simulated with random logic (not deterministic, not production-grade).
- No persistent database/storage layer.
- No authentication/authorization.
- PDF download is currently a mock byte payload.
- Backend is not yet integrated into frontend workflow.

---

## Suggested Next Enhancements

- Replace randomized validation with deterministic rule engine + external API connectors.
- Integrate backend validation endpoints and move business logic out of Streamlit UI layer.
- Add unit/integration tests for scoring and risk assignment.
- Add audit logs and explainability records for compliance workflows.
- Export true PDF reports (templated summaries + evidence).
- Add role-based actions and reviewer queue management.

---

## Troubleshooting

- **`ModuleNotFoundError` on startup:**
  Re-run `pip install -r requirements.txt`.

- **Port conflict (`8501` or `8000` already in use):**
  Start on a different port:
  - Streamlit: `streamlit run app/main.py --server.port 8502`
  - Uvicorn: `uvicorn app.backend.main:app --reload --port 8001`

- **CSV upload issues:**
  Ensure the file is valid CSV and includes expected provider fields.

---

## License

No license file is currently included in this repository. Add one (e.g., MIT/Apache-2.0) before external distribution.


## Running the Application

### 1) Start the Streamlit UI

```bash
streamlit run app/main.py
```

Then open the local URL shown in your terminal (typically `http://localhost:8501`).

### 2) (Optional) Start the FastAPI backend

```bash
uvicorn app.backend.main:app --reload --port 8000
```

Check health/status:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{"message":"Agentic AI Backend is running."}
```
## Known Limitations

- Validation is simulated with random logic (not deterministic, not production-grade).
- No persistent database/storage layer.
- No authentication/authorization.
- PDF download is currently a mock byte payload.
- Backend is not yet integrated into frontend workflow.

---

## Suggested Next Enhancements

- Replace randomized validation with deterministic rule engine + external API connectors.
- Integrate backend validation endpoints and move business logic out of Streamlit UI layer.
- Add unit/integration tests for scoring and risk assignment.
- Add audit logs and explainability records for compliance workflows.
- Export true PDF reports (templated summaries + evidence).
- Add role-based actions and reviewer queue management.

---

## Troubleshooting

- **`ModuleNotFoundError` on startup:**
  Re-run `pip install -r requirements.txt`.

- **Port conflict (`8501` or `8000` already in use):**
  Start on a different port:
  - Streamlit: `streamlit run app/main.py --server.port 8502`
  - Uvicorn: `uvicorn app.backend.main:app --reload --port 8001`

- **CSV upload issues:**
  Ensure the file is valid CSV and includes expected provider fields.

---



