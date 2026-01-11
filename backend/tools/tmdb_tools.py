import time
from datetime import date
from typing import Literal, Optional, List, Union

import requests

from backend.clients import tmdb_client
from backend.tools.cache_utils import TimeBasedCache

movie_cache = TimeBasedCache(86400)


def get_movie_genres() -> dict:
    try:
        data = tmdb_client.fetch_tmdb_genres()
        genres = data.get("genres", [])
        return {g["name"]: g["id"] for g in genres}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching genres: {e}")
        return {}


def search_movies_by_genre(
    genre_name: Optional[Union[str, List[str]]] = None,
    sort_by: Literal["latest", "popular"] = "latest",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    excluded_genres: Optional[List[str]] = None,
    page: int = 1
) -> list:
    master_cache_key = f"master_movies_{sort_by}_{start_date}_{end_date}"
    
    cached_master_list = movie_cache.get(master_cache_key)
    
    if not cached_master_list:
        print("Fetching master list from TMDB...")
        cached_master_list = _fetch_movies_from_api(
            sort_by=sort_by,
            start_date=start_date,
            end_date=end_date,
            limit=300
        )
        movie_cache.set(master_cache_key, cached_master_list)
    
    filtered_movies = _filter_movies(cached_master_list, genre_name, excluded_genres)
    
    return filtered_movies[:limit]


def _fetch_movies_from_api(
    sort_by: str,
    start_date: Optional[str],
    end_date: Optional[str],
    limit: int
) -> list:
    today = date.today().isoformat()

    if sort_by == "popular":
        tmdb_sort = "vote_average.desc"
        min_votes = 500
    else:
        tmdb_sort = "primary_release_date.desc"
        min_votes = 50

    params = {
        "sort_by": tmdb_sort,
        "primary_release_date.lte": today,
        "with_runtime.gte": 60,
        "vote_count.gte": min_votes,
        "language": "en-US",
        "page": 1
    }

    if sort_by == "popular":
        params["vote_average.gte"] = 6.5

    if start_date:
        params["primary_release_date.gte"] = start_date
    if end_date:
        params["primary_release_date.lte"] = end_date

    genre_map = get_movie_genres()
    genre_map_lower = {k.lower(): v for k, v in genre_map.items()}
    id_to_name = {v: k for k, v in genre_map.items()}
    
    try:
        movies = []
        current_page = 1

        while len(movies) < limit:
            params["page"] = current_page
            data = tmdb_client.fetch_tmdb_movies(params)
            results = data.get("results", [])

            if not results:
                break

            romance_id = genre_map_lower.get("romance")
            music_id = genre_map_lower.get("music")

            for movie in results:
                if len(movies) >= limit:
                    break

                movie_genre_ids = movie.get("genre_ids", [])

                has_romance = romance_id and romance_id in movie_genre_ids
                has_music = music_id and music_id in movie_genre_ids

                other_genres = [gid for gid in movie_genre_ids if gid != romance_id and gid != music_id]

                if other_genres:
                    if has_romance:
                        movie_genre_ids = [gid for gid in movie_genre_ids if gid != romance_id]
                    if has_music:
                        movie_genre_ids = [gid for gid in movie_genre_ids if gid != music_id]

                genre_names = [id_to_name.get(gid) for gid in movie_genre_ids if gid in id_to_name]

                poster_path = movie.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

                movies.append({
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "release_date": movie.get("release_date"),
                    "rating": movie.get("vote_average"),
                    "votes": movie.get("vote_count"),
                    "genre_ids": movie_genre_ids,
                    "genres": genre_names,
                    "poster_url": poster_url
                })

            current_page += 1
            if current_page > 20:
                break
        
        return movies

    except requests.exceptions.RequestException as e:
        print(f"Error searching movies: {e}")
        return []


def _filter_movies(
    movies: list,
    genre_name: Optional[Union[str, List[str]]],
    excluded_genres: Optional[List[str]]
) -> list:
    if not genre_name and not excluded_genres:
        return movies

    genre_map = get_movie_genres()
    genre_map_lower = {k.lower(): v for k, v in genre_map.items()}

    include_ids = set()
    if genre_name:
        if isinstance(genre_name, str):
            genre_name = [genre_name]
        for g_name in genre_name:
            if g_name.lower() not in ["none", "all", "any"]:
                g_id = genre_map_lower.get(g_name.lower())
                if g_id:
                    include_ids.add(g_id)

    exclude_ids = set()
    if excluded_genres:
        for g_name in excluded_genres:
            g_id = genre_map_lower.get(g_name.lower())
            if g_id:
                exclude_ids.add(g_id)

    filtered = []
    for movie in movies:
        movie_genre_ids = set(movie.get("genre_ids", []))
        
        if exclude_ids and not movie_genre_ids.isdisjoint(exclude_ids):
            continue
            
        if include_ids and not include_ids.issubset(movie_genre_ids):
            continue
            
        filtered.append(movie)
        
    return filtered
