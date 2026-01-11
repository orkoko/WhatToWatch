import time
from typing import Optional, List, Union

import requests

from backend.clients import jikan_client
from backend.tools.cache_utils import TimeBasedCache

anime_cache = TimeBasedCache(86400)


def get_anime_genres() -> dict:
    try:
        data = jikan_client.fetch_jikan_genres()
        genres = data.get("data", [])
        return {g["name"]: g["mal_id"] for g in genres}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching anime genres: {e}")
        return {}


def search_anime_by_genre(
    genre_name: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    excluded_genres: Optional[List[str]] = None
) -> list:
    master_cache_key = f"master_anime_{start_date}_{end_date}"
    
    cached_master_list = anime_cache.get(master_cache_key)
    
    if not cached_master_list:
        print("Fetching master anime list from Jikan...")
        cached_master_list = _fetch_anime_from_api(
            start_date=start_date,
            end_date=end_date,
            limit=300
        )
        anime_cache.set(master_cache_key, cached_master_list)
    
    filtered_anime = _filter_anime(cached_master_list, genre_name, excluded_genres)
    
    return filtered_anime[:limit]


def _fetch_anime_from_api(
    start_date: Optional[str],
    end_date: Optional[str],
    limit: int
) -> list:
    params = {
        "order_by": "score",
        "sort": "desc",
        "min_score": 6.5,
        "limit": 25,
        "page": 1,
        "type": "tv"
    }

    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    try:
        anime_list = []
        current_page = 1

        while len(anime_list) < limit:
            params["page"] = current_page
            data = jikan_client.fetch_jikan_anime(params)
            results = data.get("data", [])

            if not results:
                break

            for anime in results:
                if len(anime_list) >= limit:
                    break

                genres = [g["name"] for g in anime.get("genres", [])]

                images = anime.get("images", {})
                jpg_images = images.get("jpg", {})
                poster_url = jpg_images.get("large_image_url") or jpg_images.get("image_url")

                aired = anime.get("aired", {})
                release_date = aired.get("from", "").split("T")[0] if aired.get("from") else "Unknown"

                anime_list.append({
                    "id": anime.get("mal_id"),
                    "title": anime.get("title_english") or anime.get("title"),
                    "release_date": release_date,
                    "rating": anime.get("score"),
                    "votes": anime.get("scored_by"),
                    "genres": genres,
                    "poster_url": poster_url
                })

            current_page += 1
            if current_page > 15:
                break

            time.sleep(0.5)

        return anime_list

    except requests.exceptions.RequestException as e:
        print(f"Error searching anime: {e}")
        return []


def _filter_anime(
    anime_list: list,
    genre_name: Optional[Union[str, List[str]]],
    excluded_genres: Optional[List[str]]
) -> list:
    if not genre_name and not excluded_genres:
        return anime_list

    include_names = set()
    if genre_name:
        if isinstance(genre_name, str):
            genre_name = [genre_name]
        for g in genre_name:
            if g.lower() not in ["none", "all", "any"]:
                include_names.add(g.lower())

    exclude_names = set()
    if excluded_genres:
        for g in excluded_genres:
            exclude_names.add(g.lower())

    filtered = []
    for anime in anime_list:
        anime_genres_lower = {g.lower() for g in anime.get("genres", [])}
        
        if exclude_names and not anime_genres_lower.isdisjoint(exclude_names):
            continue
            
        if include_names and not include_names.issubset(anime_genres_lower):
            continue
            
        filtered.append(anime)
        
    return filtered
