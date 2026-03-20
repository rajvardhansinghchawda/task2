# ATS Integration Microservice (Workable) — Serverless + Python

This microservice exposes a **unified REST API** for **Jobs**, **Candidates**, and **Applications**, while internally integrating with the **Workable ATS**.

## Requirements covered

- **GET `/jobs`**: list open jobs (standard schema)
- **POST `/candidates`**: create candidate + attach to job (create application)
- **GET `/applications?job_id=...`**: list applications for a job (standard schema)
- **Environment variables** for secrets (`ATS_API_KEY`, `ATS_BASE_URL`)
- **Serverless Framework** routes (`serverless.yml`)
- **Pagination** handling for Workable (`paging.next`)
- **Clean JSON errors**

## Standardized schemas

### Job

```json
{
  "id": "string",
  "title": "string",
  "location": "string",
  "status": "OPEN|CLOSED|DRAFT",
  "external_url": "string"
}
```

### Candidate create request

```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "resume_url": "string",
  "job_id": "string"
}
```

### Application

```json
{
  "id": "string",
  "candidate_name": "string",
  "email": "string",
  "status": "APPLIED|SCREENING|REJECTED|HIRED"
}
```

## Workable sandbox & API token

- **Create a Workable account / trial** from Workable.
- **Generate API token** from Workable settings (API / integrations).
- **Base URL format (required)**:
  - `ATS_BASE_URL=https://<your_subdomain>.workable.com/spi/v3`

## Setup (local)

### 1) Python dependencies

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Serverless dependencies (for offline API Gateway simulation)

Serverless Framework uses Node.js for the CLI, but your runtime code is Python.

```bash
npm init -y
npm install --save-dev serverless serverless-offline serverless-python-requirements
```

### 3) Environment variables

Create `.env` (this repo ignores it via `.gitignore`):

```env
ATS_API_KEY=your_workable_token_here
ATS_BASE_URL=https://your_subdomain.workable.com/spi/v3
```

## Run locally

### Option A: Serverless Offline (recommended)

```bash
npx serverless offline start
```

API will be at:
- `http://localhost:3000/jobs`
- `http://localhost:3000/candidates`
- `http://localhost:3000/applications?job_id=...`

### Option B: Pure-Python local simulator (optional)

```bash
python local_server.py
```

## Example calls

### 1) Get jobs

```bash
curl http://localhost:3000/jobs
```

Pick the first job’s `id` and use it as `job_id` below.

### 2) Get applications for a job

```bash
curl "http://localhost:3000/applications?job_id=JOB_SHORTCODE_HERE"
```

### 3) Create candidate + attach to job

Workable **downloads `resume_url`** and validates file type. Use a reachable URL that ends in `.pdf/.doc/.docx/.odt/.rtf/.txt`.

Also: Workable may reject duplicate emails (422). Use a unique email per run.

```bash
curl -X POST http://localhost:3000/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane+unique@example.com",
    "phone": "555-0199",
    "resume_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    "job_id": "JOB_SHORTCODE_HERE"
  }'
```

## Deploy (AWS)

```bash
npx serverless deploy --stage prod
```
