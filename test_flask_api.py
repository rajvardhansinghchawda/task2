import subprocess
import time
import requests
import sys

print("Starting Flask local server...")
proc = subprocess.Popen([sys.executable, "local_server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for Flask to boot up
time.sleep(3)

print("\n--- Testing GET /jobs ---")
try:
    response = requests.get("http://127.0.0.1:3000/jobs", timeout=10)
    print("Status:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("GET /jobs failed:", e)

print("\n--- Testing GET /applications ---")
try:
    response = requests.get("http://127.0.0.1:3000/applications?job_id=job_123", timeout=10)
    print("Status:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("GET /applications failed:", e)

print("\n--- Testing POST /candidates ---")
try:
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "123",
        "resume_url": "https://example.com",
        "job_id": "job_123"
    }
    response = requests.post("http://127.0.0.1:3000/candidates", json=payload, timeout=10)
    print("Status:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("POST /candidates failed:", e)

print("\nCleaning up server...")
proc.terminate()
print("Test complete.")
