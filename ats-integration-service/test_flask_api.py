import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
PORT = os.getenv("PORT", "3000")
BASE = f"http://127.0.0.1:{PORT}"

print("\n--- Testing GET /jobs ---")
try:
    response = requests.get(f"{BASE}/jobs", timeout=15)
    print("Status:", response.status_code)
    jobs = response.json()
    print("Response JSON:", jobs)
except Exception as e:
    print("GET /jobs failed:", e)
    raise

if response.status_code != 200:
    print(
        "\nCannot continue candidate test because /jobs did not succeed.\n"
        "Fix your .env and restart the server:\n"
        "  WORKABLE_SUBDOMAIN=piemr\n"
        "  WORKABLE_API_KEY=YOUR_TOKEN\n"
    )
    raise SystemExit(1)

print("\n--- Testing GET /applications ---")
try:
    response = requests.get(f"{BASE}/applications", timeout=15)
    print("Status:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("GET /applications failed:", e)
    raise

print("\n--- Testing POST /candidates ---")
try:
    if not isinstance(jobs, list) or not jobs:
        raise RuntimeError("No jobs returned from GET /jobs; cannot test POST /candidates")

    job_shortcode = jobs[0].get("shortcode")
    if not job_shortcode:
        raise RuntimeError("First job does not contain 'shortcode'")

    unique_email = f"john+{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "Jane Doe",
        "email": unique_email,
        "phone": "123",
        "resume_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "job_shortcode": job_shortcode,
    }
    response = requests.post(f"{BASE}/candidates", json=payload, timeout=30)
    print("Status:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("POST /candidates failed:", e)
    raise

print("\nTest complete.")
