import os


class Config:
    WORKABLE_SUBDOMAIN = os.getenv("WORKABLE_SUBDOMAIN", "").strip()
    WORKABLE_API_KEY = os.getenv("WORKABLE_API_KEY", "").strip()

    # SQLite database file (stored in project root by default)
    DB_PATH = os.getenv("DB_PATH", os.path.join(os.getcwd(), "applications.db"))

    # Flask
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "3000"))
    DEBUG = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes", "on")

