import logging
from typing import Any, Dict, List, Optional

import requests


logger = logging.getLogger(__name__)


class WorkableAPIError(Exception):
    pass


def _base_url(subdomain: str) -> str:
    sub = (subdomain or "").strip()
    if not sub:
        raise WorkableAPIError("WORKABLE_SUBDOMAIN environment variable is missing")
    return f"https://{sub}.workable.com/spi/v3"


def _headers(api_key: str) -> Dict[str, str]:
    key = (api_key or "").strip()
    if not key:
        raise WorkableAPIError("WORKABLE_API_KEY environment variable is missing")
    return {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _get(url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise WorkableAPIError("Workable API request timed out")
    except requests.exceptions.HTTPError as e:
        raise WorkableAPIError(f"Workable HTTP {e.response.status_code}: {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise WorkableAPIError(f"Network error calling Workable: {str(e)}")


def _post(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise WorkableAPIError("Workable API request timed out")
    except requests.exceptions.HTTPError as e:
        raise WorkableAPIError(f"Workable HTTP {e.response.status_code}: {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise WorkableAPIError(f"Network error calling Workable: {str(e)}")


def fetch_jobs(subdomain: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Workable: GET /jobs
    Supports pagination via paging.next (can be a full URL).
    Returns simplified list: [{title, shortcode, location}]
    """
    base = _base_url(subdomain)
    headers = _headers(api_key)

    jobs: List[Dict[str, Any]] = []
    next_url: Optional[str] = f"{base}/jobs"
    params: Optional[Dict[str, Any]] = {"limit": 100}

    while next_url:
        data = _get(next_url, headers=headers, params=params)
        batch = data.get("jobs") or []
        for j in batch:
            loc = j.get("location")
            if isinstance(loc, dict):
                city = (loc.get("city") or "").strip()
                country = (loc.get("country") or "").strip()
                location_str = ", ".join([p for p in [city, country] if p]) or ""
            else:
                location_str = str(loc or "")

            jobs.append(
                {
                    "title": j.get("title", ""),
                    "shortcode": j.get("shortcode", ""),
                    "location": location_str,
                }
            )

        paging = data.get("paging") or {}
        next_url = paging.get("next")
        params = None  # paging.next already contains tokens

    return jobs


def create_candidate(
    subdomain: str,
    api_key: str,
    job_shortcode: str,
    name: str,
    email: str,
    resume_url: str,
    phone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Workable: POST /jobs/{shortcode}/candidates
    """
    base = _base_url(subdomain)
    headers = _headers(api_key)

    url = f"{base}/jobs/{job_shortcode}/candidates"
    payload: Dict[str, Any] = {
        "candidate": {
            "name": name,
            "email": email,
            "resume_url": resume_url,
        }
    }
    if phone:
        payload["candidate"]["phone"] = phone

    logger.info("Posting candidate to Workable job=%s email=%s", job_shortcode, email)
    return _post(url, headers=headers, payload=payload)

