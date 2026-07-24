
import requests
import os
from dotenv import load_dotenv


load_dotenv()
api_key = str(os.getenv("GAME_API_KEY"))


def all_games(page:int, order:str):

    url = "https://api.rawg.io/api/games"
    params = {
        "key": api_key,
        "page":page,
        "ordering":order,
        "page_size": 12,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    data = data["results"]
    results = []
    for r in data:
        results.append([r["slug"], r["rating"], r["background_image"], [s["image"] for s in r["short_screenshots"]], r["id"]])

    max_pages = int(int(response.json()["count"]) / 10)

    return results, max_pages


def game_detail(id):
    url = f"https://api.rawg.io/api/games/{id}"
    params = {
        "key": api_key
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    publisher = data["publishers"][0]["name"] if data["publishers"] else "Unknown"
    genre = data["genres"][0]["name"] if data["genres"] else "No genre"
    background = data["background_image"] if data["background_image"] else "No background"

    game = [data["name"], data["metacritic"], data["rating"], background, data["released"],
            publisher, data["description_raw"], genre, data["id"]]

    return game

def game_screenshot(id):
    url = f"https://api.rawg.io/api/games/{id}/screenshots"
    params = {
        "key": api_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()["results"]
    screenshots = [s["image"] for s in data]
    return screenshots


def search_games(query,page:int):
    url = "https://api.rawg.io/api/games"
    params = {
        "key": api_key,
        "search": query,
        "page": page,
        "page_size": 12,
        "search_precise": True,
        "search_exact": True
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()["results"]
    games = []
    max_pages =int(int(response.json()["count"])/10)
    for r in data:
        games.append([r["slug"], r["rating"], r["background_image"], [s["image"] for s in r["short_screenshots"]], r["id"]])


    return games, max_pages


# print(game_detail(43252))
# print(game_screenshot(43252))
# print(all_games(page=1, order="rating"))
# print((search_games("tomb raider",1)))