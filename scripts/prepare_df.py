import pandas as pd
from pathlib import Path
import sys

# add project root to import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.config import CACHE_DIR
from src.helpers import add_decade_column

# Set the option to display all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)

# -----------------------------
# Constants / Default paths
# -----------------------------
# Root folder
ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "processed"

TMDB_DATA_FILE = CACHE_DIR / "tmdb_data.csv"

# ============================================================
# STEP 1: Retrieve all TMDB data
# ============================================================

df = pd.read_csv(TMDB_DATA_FILE)

print(f"\nTMDb metadata cache has {len(df)} movies")

#print(df.info())
#print(df.head())

# ============================================================
# STEP 2: Add extra columns and clean data
# ============================================================
print(f"\nAdding extra columns and cleaning data...")

df = add_decade_column(df).copy()

# Fix Jr. by removing the leading comma
df['actors'] = df['actors'].str.replace(', Jr.', ' Jr.')

# Add main production country (first country)
df["main_country"] = df["production_countries"].str.split(", ").str[0]

# Take the first language if multiple are listed
df["main_language"] = df["spoken_languages"].str.split(", ").str[0]

# inspect NAs
#print(df.isna().sum())

# actors
#print(df[df['actors'].isna()])
# All rows without actors seem correct, experimental or animation films

# screenwriters
#print(df[df['screenwriters'].isna()])
# Mostly are documentaries

# cinematographers
#print(df[df['cinematographers'].isna()])
# Mostly are documentaries

# spoken_languages
#print(df[df['spoken_languages'].isna()])
# no spoken dialogue

# ============================================================
# STEP 3: Save final dataframe
# ============================================================

df.to_csv(OUTPUT_DIR / "final_movies.csv", index=False)
print("\nFile update completed!")