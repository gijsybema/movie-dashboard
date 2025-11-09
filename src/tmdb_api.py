import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout
from pathlib import Path
from src.config import TMDB_API_KEY

# TMDb constants
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# caching folder
ROOT_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Functions
# -----------------------------
def search_movie(title=None, year=None, tmdb_id=None):
    """
    Search TMDb for a movie by title (and optionally year) OR fetch directly by TMDB ID.
    Returns the first match as a dict, or None if not found or an error occurs.

    Args:
        title (str, optional): Movie title (used if tmdb_id is not given)
        year (int, optional): Release year (used if tmdb_id is not given)
        tmdb_id (int, optional): TMDb movie ID (skips title/year search if provided)

    Notes:
        - the first API call (/search/movie) only returns basic info: id, title, release date.
        It does NOT include runtime, genres, spoken_languages, or credits (director, cast, crew).
        - Therefore, I make a second API call to /movie/{id} with append_to_response=credits to get these extra details.
    """
    try:
        # If tmdb_id is provided, skip search and go straight to details
        if tmdb_id is not None:
            movie_id = tmdb_id

        else:
            # Otherwise, perform search as before
            url = f"{TMDB_BASE_URL}/search/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "query": title,
            }
            if year:
                params["year"] = year

            # First API call, search for movie by title and year
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()  # Raises HTTPError for bad status codes
            results = r.json().get("results")

            # Retry without year if nothing was found
            if not results and year:
                print(f"Retrying without year for '{title}'...")
                params.pop("year")
                r = requests.get(url, params=params, timeout=5)
                r.raise_for_status()
                results = r.json().get("results")

            if not results:
                print(f"⚠️ Movie not found: '{title}' (year={year})")
                return None

            movie_id = results[0]["id"]

        # Second API call: get detailed info including runtime, genres, spoken languages, and director
        details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        details_params = {
            "api_key": TMDB_API_KEY,
            "append_to_response": "credits"  # needed for director info
        }
        r_details = requests.get(details_url, params=details_params, timeout=5)
        r_details.raise_for_status()
        details = r_details.json()

        # Extract actor(s) from credits
        actors = None
        if "credits" in details and "cast" in details["credits"]:
            acting_credits = details["credits"]
            cast = [c["name"] for c in acting_credits.get("cast", []) if c.get("name")]
            if cast:
                actors = ", ".join(filter(None, cast))  # filter out any None values

        # Extract director(s) from credits
        director = None
        if "credits" in details and "crew" in details["credits"]:
            directors = [c["name"] for c in details["credits"]["crew"] if c.get("job") == "Director"]
            if directors:
                director = ", ".join(filter(None, directors))  # filter out any None values

        # Extract screenwriters from credits
        writer_jobs = {"Writer", "Screenplay", "Story", "Novel", "Adaptation"}
        writer = None
        if "credits" in details and "crew" in details["credits"]:
            writers = [c["name"] for c in details["credits"]["crew"] if c.get("job") in writer_jobs]
            writers = list(dict.fromkeys(writers)) # remove duplicates
            if writers:
                writer = ", ".join(filter(None, writers))  # filter out any None values

        # Extract cinematographers from credits
        cinematographer_jobs = {"Director of Photography", "Cinematography"}
        cinematographer = None
        if "credits" in details and "crew" in details["credits"]:
            cinematographers = [c["name"] for c in details["credits"]["crew"] if c.get("job") in cinematographer_jobs]
            if cinematographers:
                cinematographer = ", ".join(filter(None, cinematographers))  # filter out any None values

        # Extract runtime
        runtime = details.get("runtime")

        # Extract genres as a comma-separated string
        genres_list = details.get("genres")
        genres = ", ".join(filter(None, [g.get("name") for g in genres_list])) if genres_list else None

        # Extract spoken languages as a comma-separated string
        spoken = details.get("spoken_languages")
        if spoken:
            spoken_languages = ", ".join(
                l.get("english_name") for l in spoken if l.get("english_name")
            )
        else:
            spoken_languages = None

        # Extract production countries
        countries = details.get("production_countries")
        production_countries = ", ".join(filter(None, [c.get("name") for c in countries])) if countries else None

        # Return the final dictionary
        return {
            "tmdb_id": movie_id,
            "title": details.get("title"),
            "release_date": details.get("release_date"),
            "actors": actors,
            "directors": director,
            "screenwriters": writer,
            "cinematographers": cinematographer,
            "runtime": runtime,
            "genres": genres,
            "spoken_languages": spoken_languages,
            "production_countries": production_countries,
        }

    except ConnectionError as conn_err:
        print(f"Connection Error for '{title}': {conn_err}")
    except HTTPError as http_err:
        print(f"HTTP Error for '{title}': {http_err}")
    except Timeout as timeout_err:
        print(f"Timeout Error for '{title}': {timeout_err}")
    except Exception as e:
        print(f"Unexpected error for '{title}': {e}")

    # Return None if any error occurs or no results found
    return None

# -----------------------------
# Quick test / run code
# -----------------------------
if __name__ == "__main__":

    # search movies manually
    print(search_movie(title="Chungking Express", year=1994))

    # search movie with tmdb id
    print(search_movie(tmdb_id=11104))

