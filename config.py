import os

CATEGORIES = ["hep-lat", "hep-th", "hep-ex"]
ARXIV_API_URL = "http://export.arxiv.org/api/query"
MAX_RESULTS_PER_REQUEST = 100
AUTHORS_CAP = 2
FETCH_DELAY = 3  # seconds between API requests

BASE_DIR = os.path.expanduser("~/sci_read")
DB_PATH = os.path.join(BASE_DIR, "db", "papers.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
REPO_DIR = BASE_DIR
