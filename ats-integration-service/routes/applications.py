import logging

from flask import Blueprint, current_app

from database.db import list_applications
from utils.response import error, ok


logger = logging.getLogger(__name__)

applications_bp = Blueprint("applications", __name__)


@applications_bp.get("/applications")
def get_applications():
    try:
        conn = current_app.config["DB_CONN"]
        apps = list_applications(conn)
        return ok(apps)
    except Exception:
        logger.exception("Unexpected error in GET /applications")
        return error("Internal server error", 500)

