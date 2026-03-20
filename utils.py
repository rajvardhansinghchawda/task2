import json
import logging

# Configure basic logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def success_response(data):
    """
    Format a standardized successful JSON response for API Gateway.
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }

def error_response(message, status_code=500):
    """
    Format a standardized error JSON response for API Gateway.
    """
    logger.error(f"Error {status_code}: {message}")
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"error": message})
    }

def transform_job(raw_job):
    """
    Transform Workable job data into the standardized format.
    
    Workable structure:
    'shortcode', 'title', 'location', 'state', 'url'
    """
    location_obj = raw_job.get("location", {})
    location_str = ""
    
    if isinstance(location_obj, dict):
        # Workable locations have standard keys
        city = location_obj.get("city", "")
        country = location_obj.get("country", "")
        if city and country:
            location_str = f"{city}, {country}"
        elif city:
            location_str = city
        else:
            location_str = country

    status_raw = str(raw_job.get("state", "published")).upper()
    
    # Map Workable 'published' -> 'OPEN', 'draft' -> 'DRAFT', etc.
    if status_raw == "PUBLISHED":
        status_map = "OPEN"
    elif status_raw == "DRAFT":
        status_map = "DRAFT"
    elif status_raw in ["CLOSED", "ARCHIVED"]:
        status_map = "CLOSED"
    else:
        status_map = "OPEN" # Default fallback
        
    return {
        "id": str(raw_job.get("shortcode", "")),
        "title": raw_job.get("title", ""),
        "location": location_str,
        "status": status_map,
        "external_url": raw_job.get("url", "")
    }

def transform_application(raw_application):
    """
    Transform Workable application data into the standardized format.
    Workable refers to applications as 'candidates' explicitly tied to jobs.
    """
    # In Workable, standard candidates listed under a job have these fields natively:
    candidate_name = raw_application.get("name", "")
    email = raw_application.get("email", "")

    # Workable manages candidate status using 'stage'
    stage = str(raw_application.get("stage", "sourced")).upper()
    
    if stage in ["SOURCED", "APPLIED"]:
        status_map = "APPLIED"
    elif stage in ["PHONE SCREEN", "INTERVIEW", "EXECUTIVE INTERVIEW"]:
        status_map = "SCREENING"
    elif stage in ["REJECTED", "WITHDRAWN"]:
        status_map = "REJECTED"
    elif stage in ["HIRED", "OFFER"]:
        status_map = "HIRED"
    else:
        status_map = "APPLIED"

    return {
        "id": str(raw_application.get("id", "")),
        "candidate_name": candidate_name,
        "email": email,
        "status": status_map
    }
