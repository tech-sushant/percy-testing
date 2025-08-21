import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:5173"
SUPERUSER_EMAIL = os.getenv("FIRST_SUPERUSER", "admin@example.com")
SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "changethis")
