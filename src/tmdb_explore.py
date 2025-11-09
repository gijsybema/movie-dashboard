# -- TMDB EXPLORE --
# helper functions to explore the tmdb API
import requests
from src.config import TMDB_API_KEY
from pathlib import Path

# TMDb constants
TMDB_BASE_URL = "https://api.themoviedb.org/3"

ROOT_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Functions
# -----------------------------

def search_movies_raw(title, year=None):
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
    return results

def get_movie_details_raw(movie_id, append_credits=True):
    params = {"api_key": TMDB_API_KEY}
    if append_credits:
        params['append_to_response'] = 'credits'
    details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    r = requests.get(details_url, params=params, timeout=5)
    r.raise_for_status()
    details = r.json()
    return details

def get_credits_raw(movie_id):
    params = {"api_key": TMDB_API_KEY}
    credits_url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
    r = requests.get(credits_url, params=params, timeout=5)
    r.raise_for_status()
    credits = r.json()
    return credits

# -----------------------------
# Test code
# -----------------------------
# Only runs when the file is executed directly, not when imported
if __name__ == "__main__":
    from pprint import pprint
    from requests.exceptions import HTTPError, ConnectionError, Timeout

    try:
        print("Searching for movie...")
        results = search_movies_raw("Uzak")
        if not results:
            print(" No results found.")
            exit()

        movie = results[0]  # Take the first match
        movie_id = movie['id']

        print("\nFirst match:")
        print("ID:", movie_id)
        print("Title:", movie.get('title'))
        print("Overview:", movie.get('overview')[:200], "...")  # Truncate for readability

        # Details
        details = get_movie_details_raw(movie_id, append_credits=False)
        print("\nDetails:")
        print("Runtime:", details.get("runtime"), "minutes")
        print("Genres:", [g['name'] for g in details.get("genres", [])])
        print("Languages:", [l['english_name'] for l in details.get("spoken_languages", [])])
        countries = details.get("production_countries")
        production_countries = ", ".join(filter(None, [c.get("name") for c in countries])) if countries else None
        print("Countries:", production_countries)
        production_countries_iso = ", ".join(filter(None, [c.get("iso_3166_1") for c in countries])) if countries else None
        print("ISO: ", production_countries_iso)

        # optional: prettyprint the whole details JSON
        #pprint(details)

        # Credits
        print("\nCredits:")
        credits = get_credits_raw(movie_id)

        # optional: prettyprint the whole credits JSON
        #pprint(credits)

        # Cast
        cast_actors = [c["name"] for c in credits.get("cast", []) if c.get("name")] # skips all cast where name is missing or None
        print("Actors:", cast_actors[:10])

        crew_jobs = sorted({c["job"] for c in credits.get("crew", []) if c.get("job")})
        print("Crew job types:", crew_jobs)

        director = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"]
        print("Director:", director)
        cinematographer = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director of Photography"]
        print("Director of Photography:", cinematographer)

        writer_jobs = {"Writer", "Screenplay", "Story"}
        screenwriters  = [c["name"] for c in credits.get("crew", []) if c.get("job") in writer_jobs]
        screenwriters = list(dict.fromkeys(screenwriters))  # remove duplicates
        print("Screenplay:", screenwriters)

    except (HTTPError, ConnectionError, Timeout) as net_err:
        print("Network error:", net_err)
    except Exception as e:
        print("Unexpected error:", e)

