import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_URL = os.getenv("API_URL")
DEFAULT_X_HPR_ID = os.getenv("X_HPR_ID")
