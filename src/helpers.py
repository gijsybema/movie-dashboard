import pycountry
from pathlib import Path
import pandas as pd

# root folder
ROOT_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Functions
# -----------------------------

def get_language_name(iso_code):
    """
    Convert a TMDb ISO 639-1 language code to the English language name.
    Returns None if the code is invalid or not found.
    """
    if not iso_code:
        return None
    try:
        lang = pycountry.languages.get(alpha_2=iso_code)
        return lang.name if lang else None
    except:
        return None

def add_decade_column(df, date_col="release_date"):
    """
    Add a 'decade' column based on the release year.
    Example: 1987 -> 1980s
    """
    df = df.copy()
    if date_col in df.columns:
        df["year"] = pd.to_datetime(df[date_col], errors="coerce").dt.year
        df["decade"] = (
            (df["year"] // 10 * 10)
            .astype("Int64")
            .astype(str)
            .str.cat(["s"] * len(df), na_rep="")
        )
    return df

# -----------------------------
# Test code
# -----------------------------
# Only runs when the file is executed directly, not when imported
if __name__ == "__main__":
    # clean up cache (comment out if not using)
    #cleanup_cache_dir()
    exit()

    # Quick tests for get_language_name
    print("Testing get_language_name...")

    test_cases = {
        "en": "English",
        "es": "Spanish",
        "zh": "Chinese",
        "fr": "French",
        "xx": None,      # invalid code
        "": None,          # empty string
        None: None       # None
    }

    for code, expected in test_cases.items():
        result = get_language_name(code)
        print(f"{code}: {result} (expected: {expected})")
        assert result == expected, f"Failed for {code}: got {result}, expected {expected}"

    print("All tests passed!")