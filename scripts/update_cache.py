import pandas as pd
import json
import requests
import time
from tqdm import tqdm
from pathlib import Path
from random import uniform
import random
import sys

# add project root to import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.tmdb_api import search_movie
from src.config import CACHE_DIR

# -----------------------------
# Constants / Default paths
# -----------------------------
# Root folder
DATA_DIR = ROOT_DIR / "data" / "raw"

MOVIES_CSV = DATA_DIR / "sample_movies.csv"
TMDB_DATA_FILE = CACHE_DIR / "tmdb_data.csv"

# ============================================================
# STEP 1: Load Sample Data
# ============================================================
movies_df = pd.read_csv(MOVIES_CSV)
print(f"Loaded {len(movies_df)} sample movies:")
print(movies_df.head())

# ============================================================
# STEP 2: FETCH TMDb METADATA (TMDb API)
# ============================================================
print("\n=== Step 2: Fetching TMDb metadata ===")

# Load existing TMDb data if available
if TMDB_DATA_FILE.exists():
    existing_df = pd.read_csv(TMDB_DATA_FILE)
    existing_ids = set(existing_df["tmdb_id"].dropna().astype(int).tolist())
    print(f"Loaded {len(existing_ids)} existing TMDb records")
else:
    existing_df = pd.DataFrame()
    existing_ids = set()
    print("No existing TMDb data found — starting fresh")

# Determine which IDs still need fetching
remaining_ids = [int(v) for v in movies_df["tmdb_id"] if int(v) not in existing_ids]
total_missing_metadata = len(remaining_ids)
print(f"Total films missing metadata: {total_missing_metadata}\n")

# Initialize counters (reuse same logic)
found_count = 0
not_found_count = 0
new_records = []
start_time = time.time()

for tmdb_id in tqdm(remaining_ids, desc="Fetching TMDb metadata"):
    movie_data = search_movie(tmdb_id=tmdb_id)
    if movie_data:
        new_records.append(movie_data)
        found_count += 1
    else:
        not_found_count += 1
        print(f"⚠️ Skipped TMDb ID {tmdb_id} (no data or error)")

    # Save progress every 50
    if (found_count + not_found_count) % 25 == 0 and new_records:
        # build new_df and merge with existing_df (existing_df may be empty)
        new_df = pd.DataFrame(new_records)
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.drop_duplicates(subset=["tmdb_id"], inplace=True)
        else:
            combined_df = new_df
        combined_df.to_csv(TMDB_DATA_FILE, index=False)
        print(f"💾 Saved progress after {(found_count + not_found_count)} films")
        # update in-memory existing_df and clear new_records
        existing_df = combined_df
        new_records.clear()
    time.sleep(uniform(2.5, 5))  # random delay between requests

# final: if any remaining new_records: Merge and save
if new_records:
    new_df = pd.DataFrame(new_records)
    if not existing_df.empty:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    else:
        combined_df = new_df

    combined_df.drop_duplicates(subset=["tmdb_id"], inplace=True)
    combined_df.to_csv(TMDB_DATA_FILE, index=False)
    print(f"✅ Saved {len(new_records)} new entries (total {len(combined_df)}) → {TMDB_DATA_FILE}")
else:
    print("✅ No new metadata to fetch — all up to date.")

elapsed = time.time() - start_time
print("\n=== Step 2 Summary ===")
print(f"Loop finished in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
print(f"Total films processed: {found_count + not_found_count}")
print(f"✅ Metadata fetched: {found_count}")
print(f"❌ Failed fetches: {not_found_count}")
print(f"Remaining missing metadata: {total_missing_metadata - found_count}")

# -----------------------------
# Inspect TMDb metadata cache
# -----------------------------
if TMDB_DATA_FILE.exists():
    tmdb_df = pd.read_csv(TMDB_DATA_FILE)
    print(f"\nTMDb metadata cache has {len(tmdb_df)} movies")
    print("Columns in TMDb metadata:", tmdb_df.columns.tolist())
    print("First 5 rows:")
    print(tmdb_df.head())
else:
    print("\nTMDb metadata cache file does not exist yet.")

print("Cache update completed!")
