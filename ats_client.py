import os
import requests
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Workable API Requires a Bearer Token and the full base URL including subdomain
# e.g., https://your_subdomain.workable.com/spi/v3
API_KEY = os.environ.get("ATS_API_KEY")
BASE_URL = os.environ.get("ATS_BASE_URL", "").rstrip("/")

class ATSAPIError(Exception):
    """Exception raised for errors in the ATS API response."""
    pass

def _get_headers():
    if not API_KEY:
        raise ValueError("ATS_API_KEY environment variable is missing")
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def _make_get_request(endpoint, params=None):
    """Helper method to make GET requests to the Workable ATS."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=_get_headers(), params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise ATSAPIError("ATS API request timed out")
    except requests.exceptions.HTTPError as e:
        raise ATSAPIError(f"HTTP Error from ATS: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise ATSAPIError(f"Error communicating with ATS: {str(e)}")

def _make_post_request(endpoint, payload):
    """Helper method to make POST requests to the Workable ATS."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, headers=_get_headers(), json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise ATSAPIError("ATS API request timed out")
    except requests.exceptions.HTTPError as e:
        raise ATSAPIError(f"HTTP Error from ATS: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise ATSAPIError(f"Error communicating with ATS: {str(e)}")

def fetch_jobs():
    """
    Fetch jobs from the Workable API.
    Workable returns jobs under a 'jobs' key and uses 'paging.next' for pagination.
    """
    all_jobs = []
    
    # Workable returns up to 50 items per page by default.
    url_path = "/jobs"
    params = {"limit": 100}
    
    while url_path:
        # Instead of 'page=1', Workable uses URL tokens for the next page
        path = url_path if url_path.startswith("/") else f"/{url_path.split(BASE_URL)[-1].lstrip('/')}"
        
        data = _make_get_request(path, params=params)
        if not data or not isinstance(data, dict):
            break
        
        jobs_batch = data.get("jobs") or []
        all_jobs.extend(jobs_batch)
        
        # Workable pagination check
        paging = data.get("paging") or {}
        url_path = paging.get("next")
        params = None # The 'next' URL already contains limit tokens

    return all_jobs

def create_candidate(candidate_data):
    """
    For Workable, candidates are typically created directly under a job.
    We return the candidate data to be used in the next attachment step.
    """
    return {"id": "TEMP_ID", "candidate_data": candidate_data}

def attach_candidate_to_job(candidate_response, job_id):
    """
    Create a candidate entirely and attach them to the job at the same time.
    Workable endpoint: POST /jobs/{shortcode}/candidates
    """
    candidate_data = candidate_response.get("candidate_data", {})
    
    candidate_payload = {
        "candidate": {
            "name": candidate_data.get("name", ""),
            "email": candidate_data.get("email", ""),
            "phone": candidate_data.get("phone", ""),
            "resume_url": candidate_data.get("resume_url", "")
        }
    }
    
    # Note: 'job_id' in Workable is referred to as 'shortcode'
    endpoint = f"/jobs/{job_id}/candidates"
    return _make_post_request(endpoint, candidate_payload)


def fetch_applications(job_id):
    """
    Fetch all candidates (applications) for a specific job from Workable.
    Endpoint: GET /jobs/{shortcode}/candidates
    """
    all_applications = []
    
    url_path = f"/jobs/{job_id}/candidates"
    params = {"limit": 100}
    
    while url_path:
        path = url_path if url_path.startswith("/") else f"/{url_path.split(BASE_URL)[-1].lstrip('/')}"
        
        data = _make_get_request(path, params=params)
        if not data or not isinstance(data, dict):
            break
            
        apps_batch = data.get("candidates") or []
        all_applications.extend(apps_batch)
        
        paging = data.get("paging") or {}
        url_path = paging.get("next")
        params = None

    return all_applications
