import os
from dotenv import load_dotenv

load_dotenv()

API_SECRET = os.getenv("API_SECRET")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "listed.csv")
