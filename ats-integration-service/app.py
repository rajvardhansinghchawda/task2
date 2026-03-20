import logging

from dotenv import load_dotenv
from flask import Flask

import os
from database.db import get_connection, init_db
from routes.applications import applications_bp
from routes.candidates import candidates_bp
from routes.jobs import jobs_bp


def create_app() -> Flask:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)

    # Import after load_dotenv so Config reads .env values
    from config import Config

    app = Flask(__name__)
    app.config.from_object(Config)
    # Ensure values are read from current environment even if config module was imported earlier
    app.config["WORKABLE_SUBDOMAIN"] = os.getenv("WORKABLE_SUBDOMAIN", "").strip()
    app.config["WORKABLE_API_KEY"] = os.getenv("WORKABLE_API_KEY", "").strip()
    app.config["DB_PATH"] = os.getenv("DB_PATH", app.config["DB_PATH"])

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logging.getLogger(__name__).info(
        "Config loaded: subdomain=%s api_key_present=%s db_path=%s",
        app.config.get("WORKABLE_SUBDOMAIN") or "",
        bool(app.config.get("WORKABLE_API_KEY")),
        app.config.get("DB_PATH"),
    )

    # Database
    conn = get_connection(app.config["DB_PATH"])
    init_db(conn)
    app.config["DB_CONN"] = conn

    # Routes
    app.register_blueprint(jobs_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(applications_bp)

    return app


app = create_app()


if __name__ == "__main__":
    from config import Config
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, use_reloader=False)

