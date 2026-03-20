import json
import logging
from ats_client import (
    fetch_jobs, 
    create_candidate as api_create_candidate, 
    attach_candidate_to_job, 
    fetch_applications, 
    ATSAPIError
)
from utils import (
    success_response, 
    error_response, 
    transform_job, 
    transform_application
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_jobs(event, context):
    """
    GET /jobs
    Fetch open jobs from the ATS and return them in a standardized JSON format.
    """
    logger.info("Received request for GET /jobs")
    try:
        raw_jobs = fetch_jobs()
        standardized_jobs = [transform_job(job) for job in raw_jobs]
        return success_response(standardized_jobs)
    
    except ATSAPIError as e:
        logger.error(f"ATS API Error: {str(e)}")
        return error_response(str(e), status_code=502)
    except Exception as e:
        logger.exception("Unexpected error in get_jobs")
        return error_response(f"Internal server error: {str(e)}", status_code=500)

def create_candidate(event, context):
    """
    POST /candidates
    Step 1: Create candidate in ATS
    Step 2: Attach candidate to the job
    """
    logger.info("Received request for POST /candidates")
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return error_response("Invalid JSON body", status_code=400)

    # Validate required fields
    required_fields = ["name", "email", "phone", "resume_url", "job_id"]
    missing_fields = [field for field in required_fields if not body.get(field)]
    if missing_fields:
        return error_response(f"Missing required fields: {', '.join(missing_fields)}", status_code=400)

    try:
        # Step 1: Create candidate
        candidate_payload = {
            "name": body["name"],
            "email": body["email"],
            "phone": body["phone"],
            "resume_url": body["resume_url"]
        }
        candidate_response = api_create_candidate(candidate_payload)
        candidate_id = candidate_response.get("id")
        
        if not candidate_id:
            return error_response("Candidate created but ATS did not return an ID", status_code=502)

        # Step 2: Attach candidate to job
        attach_candidate_to_job(candidate_response, body["job_id"])

        response_data = {
            "message": "Candidate created successfully",
            "candidate_id": str(candidate_id)
        }
        return success_response(response_data)

    except ATSAPIError as e:
        logger.error(f"ATS API Error: {str(e)}")
        return error_response(str(e), status_code=502)
    except Exception as e:
        logger.exception("Unexpected error in create_candidate")
        return error_response(f"Internal server error: {str(e)}", status_code=500)

def get_applications(event, context):
    """
    GET /applications?job_id=...
    Fetch applications for a specific job.
    """
    logger.info("Received request for GET /applications")
    
    query_params = event.get("queryStringParameters") or {}
    job_id = query_params.get("job_id")
    
    if not job_id:
        return error_response("Missing required query parameter: 'job_id'", status_code=400)

    try:
        raw_applications = fetch_applications(job_id)
        standardized_apps = [transform_application(app) for app in raw_applications]
        return success_response(standardized_apps)

    except ATSAPIError as e:
        logger.error(f"ATS API Error: {str(e)}")
        return error_response(str(e), status_code=502)
    except Exception as e:
        logger.exception("Unexpected error in get_applications")
        return error_response(f"Internal server error: {str(e)}", status_code=500)
