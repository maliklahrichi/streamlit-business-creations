"""Identity block shown in the sidebar (required by the course instructor).

>>> Edit only this file to update your information. <<<
EFREI logo: assets/efrei_logo.png (shown automatically when present).
"""
from pathlib import Path

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "efrei_logo.png"

PROFILE = {
    "name": "Malik Lahrichi",
    "program": "Engineering degree – Data Engineering",
    "year": "4th year (2nd year of the engineering cycle)",
    "email": "malik.lahrichi@efrei.net",
    "linkedin": "https://www.linkedin.com/in/malik-lahrichi-585a18291/",
    "github": "https://github.com/maliklahrichi",
    "course": "Data Analysis & Visualization",
    "project": "Individual Project: Streamlit Dashboard – Data Storytelling 2026",
    "instructor": "Prof. Mano Mathew",
    "instructor_contact": "mano.mathew@efrei.fr",
}
