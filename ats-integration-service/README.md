# ATS Integration Microservice (Workable) — Flask + SQLite

Production-style Python backend that integrates with the **Workable ATS API** and provides:

- `GET /jobs` (from Workable)
- `POST /candidates` (create candidate in Workable + store application locally)
- `GET /applications` (read locally stored applications from SQLite)

## Tech stack

- Python 3.10+
- Flask
- requests
- python-dotenv
- SQLite

## Folder structure

```text
ats-integration-service/
  app.py
  config.py
  requirements.txt
  .env
  services/
    workable_service.py
  routes/
    jobs.py
    candidates.py
    applications.py
  models/
    application_model.py
  database/
    db.py
  utils/
    response.py
  test_flask_api.py
```

## Environment variables

Create/edit `.env`:

```env
WORKABLE_SUBDOMAIN=piemr
WORKABLE_API_KEY=your_api_key_here
```

Workable base URL used:

`https://{subdomain}.workable.com/spi/v3`

Auth header:

`Authorization: Bearer WORKABLE_API_KEY`

## Endpoints

### 1) GET /jobs

Fetches jobs from Workable (`GET /jobs`) and returns:

```json
[
  { "title": "Backend Developer", "shortcode": "abc123", "location": "Remote" }
]
```

### 2) POST /candidates

Creates candidate in Workable (`POST /jobs/{JOB_SHORTCODE}/candidates`), then stores the application locally.

Request body:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "123",
  "job_shortcode": "abc123",
  "resume_url": "https://example.com/resume.pdf"
}
```

Workable downloads `resume_url`. Use a reachable URL ending in: `.pdf/.doc/.docx/.odt/.rtf/.txt`

### 3) GET /applications

Returns SQLite-stored applications:

```json
[
  { "id": 1, "name": "John Doe", "email": "john@example.com", "job_shortcode": "abc123", "resume_url": "...", "created_at": "..." }
]
```

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Server runs on `http://127.0.0.1:3000`.

## Test locally

In a second terminal (with server running):

```bash
python test_flask_api.py
```
