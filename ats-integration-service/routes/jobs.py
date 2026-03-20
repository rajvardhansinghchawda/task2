import logging

from flask import Blueprint, current_app

from services.workable_service import WorkableAPIError, fetch_jobs
from utils.response import error, ok


logger = logging.getLogger(__name__)

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("/jobs")
def get_jobs():
    cfg = current_app.config
    logger.info(
        "GET /jobs config: subdomain=%s api_key_present=%s",
        cfg.get("WORKABLE_SUBDOMAIN") or "",
        bool(cfg.get("WORKABLE_API_KEY")),
    )
    try:
        jobs = fetch_jobs(cfg["WORKABLE_SUBDOMAIN"], cfg["WORKABLE_API_KEY"])
        return ok(jobs)
    except WorkableAPIError as e:
        logger.exception("Workable error in GET /jobs")
        return error(str(e), 502)
    except Exception as e:
        logger.exception("Unexpected error in GET /jobs")
        return error("Internal server error", 500)

