import streamlit as st
from pathlib import Path
import pandas as pd

from src.graphs import plot_bar, plot_map

# -----------------------------
# Constants / Default paths
# -----------------------------
# Root folder
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"

MOVIE_DATA_FILE = DATA_PROCESSED_DIR / "final_movies.csv"

# -----------------------------
# Define Dashboard function
# -----------------------------

def run_dashboard():
    st.set_page_config(page_title="Movie Dashboard", layout="wide")
    st.title("🎬 My Movie Dashboard")

    # set colors and gradients
    orange = "#FFA500"
    orange_gradient = ["#FFCC66", "#FFA500", "#FF8800"]
    blue = "#1E90FF"
    blue_gradient = ["#66B2FF",  "#1E90FF", "#125E99"]
    green = "#2BA42B"
    green_gradient = ["#70D070", "#2BA42B", "#238C23"]

    # -----------------------------
    # Load data
    # -----------------------------
    # -- DIARY --

    # -- WATCHED --
    df = pd.read_csv(MOVIE_DATA_FILE)

    # Clean data after loading
    df["genres"] = df["genres"].fillna("").astype(str)

    # -----------------------------
    # Filters
    # -----------------------------
    st.sidebar.header("🎬 Filters")

    # 1. Country Filter
    all_countries = sorted(df['main_country'].astype(str).dropna().unique())
    country_filter = st.sidebar.multiselect(
        "Production country:",
        options=all_countries,
        default=[]
    )

    # 2 USA filter
    usa_filter = st.sidebar.selectbox(
        "USA or not:",
        options=["All", "USA", "Non-USA"]
    )

    # 3. Decade filter
    decades = sorted(df["decade"].unique())
    decade_filter = st.sidebar.multiselect(
        "Decade:",
        options=decades,
        default=[]
    )

    # 4. Spoken languages filter
    all_languages = sorted(df['main_language'].astype(str).dropna().unique())
    language_filter = st.sidebar.multiselect(
        "Main Language:",
        options=all_languages,
        default=[]
    )

    # 5. Main language is English
    english_filter = st.sidebar.selectbox(
        "English as main language or not:",
        options=["All", "English", "Non-English"]
    )

    # 6. Genre filter
    all_genres = sorted(set(g.strip() for genres in df["genres"].dropna() for g in genres.split(", ")))
    genre_filter = st.sidebar.multiselect(
        "Genre:",
        options=all_genres,
        default=[]
    )

    # Apply Filters
    df_filtered = df.copy()

    # Country filter
    if country_filter:
        df_filtered = df_filtered[df_filtered["main_country"].isin(country_filter)]

    # USA filter
    if usa_filter == "USA":
        df_filtered = df_filtered[df_filtered["main_country"].str.contains("United States of America", case=False, na=False)]
    elif usa_filter == "Non-USA":
        df_filtered = df_filtered[~df_filtered["main_country"].str.contains("United States of America", case=False, na=False)]

    # Decade filter
    if decade_filter:
        df_filtered = df_filtered[df_filtered["decade"].isin(decade_filter)]

    # main languages (handle multiple)
    if language_filter:
        df_filtered = df_filtered[df_filtered["main_language"].isin(language_filter)]

    # English language filter
    if english_filter == "English":
        df_filtered = df_filtered[df_filtered["main_language"].str.contains("English", case=False, na=False)]
    elif english_filter == "Non-English":
        df_filtered = df_filtered[~df_filtered["main_language"].str.contains("English", case=False, na=False)]

    # Genre filter (handle multiple genres per movie)
    if genre_filter:
        df_filtered = df_filtered[
            df_filtered["genres"].apply(
                lambda x: isinstance(x,str) and any(g.strip() in genre_filter for g in x.split(","))
            )]

    # -----------------------------
    # Summary stats
    # -----------------------------
    st.header("Summary")
    st.write(f"Total movies watched: {len(df_filtered)}")
    #st.write(f"Total movies in diary: {len(df_diary)}")

    # -----------------------------
    # Movies watched per year
    # -----------------------------
#    st.header("Movies Watched Over Time")
#    if 'Watched Year' in df_diary.columns and not df_diary['Watched Year'].isnull().all():
#        movies_per_year = df_diary['Watched Year'].value_counts().reset_index()
#        movies_per_year.columns = ["Watched Year", "Count"]
#
#        fig = plot_bar(
#            movies_per_year,
#            x_col="Watched Year",
#            y_col="Count",
#            title="Movies Watched Over Time",
#            orientation="v",
#            order_axis=True,  # years in chronological order
#            color = orange
#        )
#        st.plotly_chart(fig, use_container_width=True)
#
#    else:
#        st.write("No Date Watched information available for plotting.")

    # -----------------------------
    # Movies per release year
    # -----------------------------
    st.header("Release Years of Movies")
    if 'year' in df_filtered.columns and not df_filtered['year'].isnull().all():
        movies_per_year = df_filtered['year'].value_counts().reset_index()
        movies_per_year.columns = ["Year", "Count"]

        fig = plot_bar(
            movies_per_year,
            x_col="Year",
            y_col="Count",
            title="Movies by Release Year",
            orientation="v",
            color = blue,
            order_axis=True  # years in chronological order
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("No release date information available for plotting.")

    # -----------------------------
    # Movies per decade
    # -----------------------------
    st.header("Movies by Decade")
    if 'decade' in df_filtered.columns and not df_filtered['decade'].isnull().all():
        movies_per_year = df_filtered['decade'].value_counts().reset_index()
        movies_per_year.columns = ["Decade", "Count"]

        fig = plot_bar(
            movies_per_year,
            x_col="Decade",
            y_col="Count",
            title="Movies by Release Year",
            orientation="v",
            color = blue_gradient,
            order_axis=False  # years in chronological order
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("No decade information available.")

    # -----------------------------
    # Languages and Genres
    # -----------------------------
    st.header("Languages and Genres of Movies")

    # create two columns
    col1, col2 = st.columns(2)

    # Movies per language
    with col1:
        if "main_language" in df_filtered.columns and not df_filtered["main_language"].isnull().all():
            lang_counts = df_filtered["main_language"].value_counts().reset_index()
            lang_counts.columns = ["Language", "Count"]

            fig = plot_bar(lang_counts, x_col="Count", y_col="Language", orientation="h"
                           , title="Top 10 Languages", top_n=10, color=green_gradient)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.write("No spoken language data available.")

    # Movies per genre
    with col2:
        if "genres" in df_filtered.columns and not df_filtered["genres"].isnull().all():
            genre_exploded = df_filtered.assign(
                Genre_List=df_filtered["genres"].str.split(", ")
            ).explode("Genre_List")

            genre_counts = genre_exploded["Genre_List"].value_counts().reset_index()
            genre_counts.columns = ["Genre", "Count"]

            fig = plot_bar(genre_counts, x_col="Count", y_col="Genre", orientation="h"
                           , title="Top 10 Genres", top_n=10, color=green_gradient)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No genre data available.")

    # -----------------------------
    # Cast and Crew
    # -----------------------------
    st.header("Cast and Crew")

    # create two columns
    col1, col2 = st.columns(2)

    # Most common directors
    with col1:
        if "directors" in df_filtered.columns and not df_filtered["directors"].isnull().all():
            # Store all directors in separate rows if film has multiple directors
            directors_exploded = df_filtered.assign(
                Director_List=df_filtered["directors"].str.split(", ")
            ).explode("Director_List")

            director_counts = directors_exploded["Director_List"].value_counts().reset_index()
            director_counts.columns = ["Director", "Count"]

            fig = plot_bar(director_counts, x_col="Count", y_col="Director", orientation="h"
                           , top_n = 10, title="Top 10 Directors", color=blue_gradient)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.write("No director data available.")

    # Most common actors
    with col2:
        if "actors" in df_filtered.columns and not df_filtered["actors"].isnull().all():
            # Store all actors in separate rows
            actors_exploded = df_filtered.assign(
                Actor_List=df_filtered["actors"].str.split(", ")
            ).explode("Actor_List")

            actors_counts = actors_exploded["Actor_List"].value_counts().reset_index()
            actors_counts.columns = ["Actor", "Count"]

            fig = plot_bar(actors_counts, x_col="Count", y_col="Actor", orientation="h"
                           , title="Top 10 Actors", top_n=10, color=green_gradient)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No actor data available.")

    # create two columns
    col1, col2 = st.columns(2)

    # Most common screenwriters
    with col1:
        if "screenwriters" in df_filtered.columns and not df_filtered["screenwriters"].isnull().all():
            # Store all screenwriters in separate rows if film has multiple screenwriters
            screenwriters_exploded = df_filtered.assign(
                Screenwriter_List=df_filtered["screenwriters"].str.split(", ")
            ).explode("Screenwriter_List")

            screenwriter_counts = screenwriters_exploded["Screenwriter_List"].value_counts().reset_index()
            screenwriter_counts.columns = ["Screenwriter", "Count"]

            fig = plot_bar(screenwriter_counts, x_col="Count", y_col="Screenwriter", orientation="h"
                           , top_n = 10, title="Top 10 Screenwriters", color=blue_gradient)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.write("No screenwriter data available.")

    # Most common cinematographers
    with col2:
        if "cinematographers" in df_filtered.columns and not df_filtered["cinematographers"].isnull().all():
            # Store all cinematographers in separate rows if film has multiple cinematographers
            cinematographers_exploded = df_filtered.assign(
                Cinematographer_List=df_filtered["cinematographers"].str.split(", ")
            ).explode("Cinematographer_List")

            cinematographer_counts = cinematographers_exploded["Cinematographer_List"].value_counts().reset_index()
            cinematographer_counts.columns = ["Cinematographer", "Count"]

            fig = plot_bar(cinematographer_counts, x_col="Count", y_col="Cinematographer", orientation="h"
                           , title="Top 10 Cinematographers", top_n=10, color=green_gradient)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No cinematographer data available.")


    # -----------------------------
    # Movies per country
    # -----------------------------

    if "main_country" in df_filtered.columns and not df_filtered["main_country"].isnull().all():
        st.header("Movies by Country")

        col1, col2 = st.columns([1, 2])
        # Horizontal bar chart
        country_counts = df_filtered["main_country"].value_counts().reset_index()
        country_counts.columns = ["Country", "Count"]

        with col1:
            fig = plot_bar(country_counts, x_col="Count", y_col="Country", orientation="h",
                           title="Movies per Main Production Country", top_n=10, color=orange_gradient)
            st.plotly_chart(fig, use_container_width=True)

        # World map choropleth
        with col2:
            fig_map =  plot_map(country_counts,
                                country_col="Country",
                                y_col="Count",
                                title="Number of Movies per Main Production Country",
                                color=orange_gradient)
            st.plotly_chart(fig_map, use_container_width=True)

    else:
        st.write("No country data available.")

    # -----------------------------
    # Movies table
    # -----------------------------
    st.header("Watched Movies")
    st.dataframe(df_filtered)

# -----------------------------
# Optional: test dashboard locally
# -----------------------------
if __name__ == "__main__":
    run_dashboard()