import time
import requests


def fetch_jikan_genres() -> dict:
    url = "https://api.jikan.moe/v4/genres/anime"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_jikan_anime(params: dict) -> dict:
    url = "https://api.jikan.moe/v4/anime"
    response = requests.get(url, params=params)

    if response.status_code == 429:
        time.sleep(2)
        response = requests.get(url, params=params)

    response.raise_for_status()
    return response.json()
