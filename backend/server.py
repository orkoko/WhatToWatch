from datetime import date, timedelta
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.tools import tmdb_tools, jikan_tools

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/genres")
def get_genres():
    try:
        genres = tmdb_tools.get_movie_genres()
        return [{"name": name, "id": gid} for name, gid in genres.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/movies/best-last-year")
def get_best_movies_last_year(
    excluded_genres: Optional[List[str]] = Query(None),
    selected_genres: Optional[List[str]] = Query(None)
):
    try:
        start_date = (date.today() - timedelta(days=365)).isoformat()

        # Increased limit to 300 to match the "top 300" requirement
        movies = tmdb_tools.search_movies_by_genre(
            genre_name=selected_genres,
            sort_by="popular",
            start_date=start_date,
            limit=300,
            excluded_genres=excluded_genres
        )

        available_genre_ids = {
            gid for movie in movies for gid in movie.get("genre_ids", [])
        }

        all_genres = tmdb_tools.get_movie_genres()
        id_to_name = {v: k for k, v in all_genres.items()}

        available_genres_list = [
            {"id": gid, "name": id_to_name[gid]}
            for gid in available_genre_ids if gid in id_to_name
        ]
        available_genres_list.sort(key=lambda x: x["name"])

        return {
            "movies": movies,
            "available_genres": available_genres_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/anime/genres")
def get_anime_genres():
    try:
        genres = jikan_tools.get_anime_genres()
        return [{"name": name, "id": gid} for name, gid in genres.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/anime/best-last-year")
def get_best_anime_last_year(
    excluded_genres: Optional[List[str]] = Query(None),
    selected_genres: Optional[List[str]] = Query(None)
):
    try:
        start_date = (date.today() - timedelta(days=365)).isoformat()

        anime_list = jikan_tools.search_anime_by_genre(
            genre_name=selected_genres,
            start_date=start_date,
            limit=300,
            excluded_genres=excluded_genres
        )

        available_genre_names = {
            genre for anime in anime_list for genre in anime.get("genres", [])
        }

        available_genres_list = [{"name": name, "id": name} for name in available_genre_names]
        available_genres_list.sort(key=lambda x: x["name"])

        return {
            "anime": anime_list,
            "available_genres": available_genres_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
