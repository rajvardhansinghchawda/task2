import logging
import re

from flask import Blueprint, current_app, request

from database.db import insert_application
from services.workable_service import WorkableAPIError, create_candidate
from utils.response import error, ok


logger = logging.getLogger(__name__)

candidates_bp = Blueprint("candidates", __name__)


@candidates_bp.post("/candidates")
def post_candidates():
    body = request.get_json(silent=True) or {}

    required = ["name", "email", "job_shortcode", "resume_url"]
    missing = [k for k in required if not body.get(k)]
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400)

    resume_url = str(body.get("resume_url", "")).strip()
    if not re.search(r"\.(pdf|doc|docx|odt|rtf|txt)(\?.*)?$", resume_url, re.IGNORECASE):
        return error("Invalid resume_url: must end with .pdf/.doc/.docx/.odt/.rtf/.txt", 400)

    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip()
    job_shortcode = str(body.get("job_shortcode", "")).strip()
    phone = (str(body.get("phone", "")).strip() or None)

    cfg = current_app.config
    conn = current_app.config["DB_CONN"]

    try:
        workable_resp = create_candidate(
            subdomain=cfg["WORKABLE_SUBDOMAIN"],
            api_key=cfg["WORKABLE_API_KEY"],
            job_shortcode=job_shortcode,
            name=name,
            email=email,
            resume_url=resume_url,
            phone=phone,
        )

        app_id = insert_application(conn, name=name, email=email, job_shortcode=job_shortcode, resume_url=resume_url)

        candidate_id = workable_resp.get("id") or (workable_resp.get("candidate") or {}).get("id")
        return ok(
            {
                "message": "Candidate created successfully",
                "candidate_id": candidate_id,
                "application_id": app_id,
            },
            201,
        )
    except WorkableAPIError as e:
        logger.exception("Workable error in POST /candidates")
        return error(str(e), 502)
    except Exception:
        logger.exception("Unexpected error in POST /candidates")
        return error("Internal server error", 500)

