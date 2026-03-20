from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Application:
    id: int
    name: str
    email: str
    job_shortcode: str
    resume_url: str
    created_at: str

