import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Retrieve TMDB_API_KEY
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if TMDB_API_KEY is None:
    raise ValueError("TMDB_API_KEY not found. Please add it to your .env file.")

# define CACHE_DIR for tmdb_ids
CACHE_DIR = ROOT_DIR / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)