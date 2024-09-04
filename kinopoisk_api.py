import requests
from typing import Dict, Union, Optional
from config import KINOPOISK_API_KEY, KINOPOISK_BASE_URL

def search_movies(title: str = "Spider-Man", page: int = 1, limit: int = 5) -> Dict[str, Union[str, Dict]]:
    """
    Функция для поиска фильмов по запросу.

    :param title: Название фильма (или часть названия). По умолчанию 'Spider-Man'.
    :param page: Номер страницы результатов. По умолчанию 1.
    :param limit: Количество результатов на страницу. По умолчанию 5.
    :return: Результаты поиска или сообщение об ошибке.
    """
    params = {
        "query": title,
        "page": page,
        "limit": limit
    }
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": KINOPOISK_API_KEY
    }
    
    request_url = f"{KINOPOISK_BASE_URL}/search"
    
    print(f"Отправляем запрос: {request_url}?{requests.compat.urlencode(params)}")
    
    try:
        response = requests.get(request_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {"error": "Ошибка запроса к API"}
    except ValueError:
        print("Ошибка декодирования JSON.")
        return {"error": "Ошибка декодирования JSON"}

def movie_by_rating(rating_from: float = 7.0, rating_to: float = 10.0, page: int = 1, limit: int = 5) -> Dict[str, Union[str, Dict]]:
    """
    Функция для поиска фильмов по рейтингу.

    :param rating_from: Минимальный рейтинг.
    :param rating_to: Максимальный рейтинг.
    :param page: Номер страницы результатов.
    :param limit: Количество результатов на страницу.
    :return: Результаты поиска или сообщение об ошибке.
    """
    params = {
        "page": page,
        "limit": limit,
        "rating.imdb": f"{rating_from}-{rating_to}",
        "notNullFields": "name"
    }
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": KINOPOISK_API_KEY
    }
    
    request_url = KINOPOISK_BASE_URL
    
    print(f"Отправляем запрос: {request_url}?{requests.compat.urlencode(params)}")
    
    try:
        response = requests.get(request_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {"error": "Ошибка запроса к API"}
    except ValueError:
        print("Ошибка декодирования JSON.")
        return {"error": "Ошибка декодирования JSON"}

def search_low_budget_movies(page: int = 1, limit: int = 5) -> Dict[str, Union[str, Dict]]:
    """
    Функция для поиска фильмов с низким бюджетом (до $10 миллионов).

    :param page: Номер страницы результатов.
    :param limit: Количество результатов на страницу.
    :return: Результаты поиска или сообщение об ошибке.
    """
    params = {
        "budget.value": "0-10000000",
        "page": page,
        "limit": limit,
        "notNullFields": "name"
    }
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": KINOPOISK_API_KEY
    }
    
    request_url = KINOPOISK_BASE_URL
    
    print(f"Отправляем запрос: {request_url}?{requests.compat.urlencode(params)}")
    
    try:
        response = requests.get(request_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {"error": "Ошибка запроса к API"}
    except ValueError:
        print("Ошибка декодирования JSON.")
        return {"error": "Ошибка декодирования JSON"}

def search_high_budget_movies(page: int = 1, limit: int = 5) -> Dict[str, Union[str, Dict]]:
    
    params = {
        "budget.value": "100000000-100000000000",
        "page": page,
        "limit": limit,
        "notNullFields": "name"
    }
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": KINOPOISK_API_KEY
    }
    
    request_url = KINOPOISK_BASE_URL
    
    print(f"Отправляем запрос: {request_url}?{requests.compat.urlencode(params)}")
    
    try:
        response = requests.get(request_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {"error": "Ошибка запроса к API"}
    except ValueError:
        print("Ошибка декодирования JSON.")
        return {"error": "Ошибка декодирования JSON"}

def search_movies_by_year(year_start: Optional[int] = None, year_end: Optional[int] = None, page: int = 1, limit: int = 5) -> Dict[str, Union[str, Dict]]:
    
    year_range = f"{year_start}-{year_end}" if year_start and year_end else ""
    params = {
        "page": page,
        "limit": limit,
        "year": year_range,
        "notNullFields": "name"
    }
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": KINOPOISK_API_KEY
    }
    
    request_url = KINOPOISK_BASE_URL
    
    print(f"Отправляем запрос: {request_url}?{requests.compat.urlencode(params)}")
    
    try:
        response = requests.get(request_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {"error": "Ошибка запроса к API"}
    except ValueError:
        print("Ошибка декодирования JSON.")
        return {"error": "Ошибка декодирования JSON"}

def search_movies_by_genre(genre: str, page: int = 1, limit: int = 5) -> Dict[str, Union[str, Dict]]:
    
    params = {
        "genres.name": genre,
        "page": page,
        "limit": limit,
        "notNullFields": "name"
    }
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": KINOPOISK_API_KEY
    }
    
    request_url = KINOPOISK_BASE_URL
    
    print(f"Отправляем запрос: {request_url}?{requests.compat.urlencode(params)}")
    
    try:
        response = requests.get(request_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {"error": "Ошибка запроса к API"}
    except ValueError:
        print("Ошибка декодирования JSON.")
        return {"error": "Ошибка декодирования JSON"}

if __name__ == "__main__":
    # Примеры вызова функций
    result_search = search_movies()
    print(result_search)
    
    result_rating = movie_by_rating(rating_from=8.0, rating_to=9.5)
    # print(result_rating)
    
    result_low_budget = search_low_budget_movies()
    # print(result_low_budget)
    
    result_high_budget = search_high_budget_movies()
    # print(result_high_budget)
    
    result_year = search_movies_by_year(year_start=2012, year_end=2012)
    # print(result_year)
    
    genres = ["Комедия", "Ужасы", "Фантастика"]
    for genre in genres:
        result_genre = search_movies_by_genre(genre=genre)
        print(f"Результаты для жанра '{genre}':")
    #     print(result_genre)
