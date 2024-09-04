import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
KINOPOISK_API_KEY = os.getenv('KINOPOISK_API_KEY')
KINOPOISK_BASE_URL = os.getenv('KINOPOISK_BASE_URL', 'https://api.kinopoisk.dev/v1.4/movie')
