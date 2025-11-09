# check_cache.py
import json
import pandas as pd
from src.config import CACHE_DIR

TMDB_ID_CACHE = CACHE_DIR / "tmdb_id_cache.json"
TMDB_DATA_CSV = CACHE_DIR / "tmdb_data.csv"

# -----------------------------
# Test code
# -----------------------------
# Only runs when the file is executed directly, not when imported
if __name__ == "__main__":
    # Load ID cache
    if TMDB_ID_CACHE.exists():
        with open(TMDB_ID_CACHE, "r", encoding="utf-8") as f:
            tmdb_id_cache = {k: v for k, v in json.load(f).items() if v}
        print(f"TMDb ID cache entries: {len(tmdb_id_cache)}")
    else:
        tmdb_id_cache = {}
        print("TMDb ID cache not found!")

    # Load metadata CSV
    if TMDB_DATA_CSV.exists():
        tmdb_data = pd.read_csv(TMDB_DATA_CSV)
        if "tmdb_id" in tmdb_data.columns:
            tmdb_data["tmdb_id"] = tmdb_data["tmdb_id"].astype(int)
            print(f"TMDb metadata rows: {len(tmdb_data)}")
        else:
            print("Warning: 'tmdb_id' column missing from metadata CSV")
            tmdb_data["tmdb_id"] = pd.Series(dtype=int)
    else:
        tmdb_data = pd.DataFrame(columns=["tmdb_id"])
        print("TMDb metadata CSV not found!")

    # Compare cache vs metadata
    cache_ids = set(int(v) for v in tmdb_id_cache.values())
    metadata_ids = set(tmdb_data["tmdb_id"].dropna().astype(int))

    matching_ids = cache_ids & metadata_ids
    missing_in_metadata = cache_ids - metadata_ids
    missing_in_cache = metadata_ids - cache_ids

    print(f"TMDb IDs present in both cache & metadata: {len(matching_ids)}")
    print(f"TMDb IDs missing in metadata CSV: {len(missing_in_metadata)}")
    print(f"TMDb IDs missing in ID cache: {len(missing_in_cache)}")
