import requests
from backend.config import config


def fetch_tmdb_genres() -> dict:
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {
        "api_key": config.TMDB_API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_tmdb_movies(params: dict) -> dict:
    url = "https://api.themoviedb.org/3/discover/movie"
    if "api_key" not in params:
        params["api_key"] = config.TMDB_API_KEY

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
