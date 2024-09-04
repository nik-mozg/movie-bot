import asyncio
import aiohttp
from datetime import datetime
from typing import Callable, Dict, Any, Optional

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

from config import TELEGRAM_TOKEN
from kinopoisk_api import (
    search_movies,
    movie_by_rating,
    search_low_budget_movies,
    search_high_budget_movies,
    search_movies_by_year,
    search_movies_by_genre,
)
from history_manager import (
    add_to_history,
    get_history_by_date,
    mark_movie_as_watched,    
)

# Создаем объект бота и диспетчер
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Константы
LIMIT = 5

# Определение состояний
class SearchState(StatesGroup):
    waiting_for_movie_title = State()
    waiting_for_rating_range = State()
    waiting_for_year = State()
    waiting_for_genre = State()
    waiting_for_history_date = State()

def get_main_menu() -> InlineKeyboardMarkup:
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Найти фильм по названию", callback_data="movie_search")
    builder.button(text="Найти фильм по рейтингу", callback_data="movie_by_rating")
    builder.button(text="Найти фильмы с низким бюджетом", callback_data="low_budget_movie")
    builder.button(text="Найти фильмы с высоким бюджетом", callback_data="high_budget_movie")
    builder.button(text="Найти фильм по году выпуска", callback_data="movie_by_year")
    builder.button(text="Найти фильм по жанру", callback_data="movie_by_genre")
    builder.button(text="История запросов", callback_data="history")
    builder.button(text="Обновить", callback_data="refresh")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: Message) -> None:
    
    await message.answer(
        "Привет! Я бот для поиска фильмов. Используй меню ниже, чтобы выбрать команду:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(lambda c: c.data in [
    "movie_search", "movie_by_rating", "low_budget_movie",
    "high_budget_movie", "movie_by_year", "movie_by_genre",
    "history", "refresh"
])
async def handle_menu_callbacks(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатия на кнопки меню, переключает состояние и инициирует соответствующие действия.
    
    Args:
        callback_query (CallbackQuery): Запрос на обработку кнопки меню.
        state (FSMContext): Контекст состояния машины состояний.
    """
    data = callback_query.data
    if data == "movie_search":
        await callback_query.message.answer("Введите название фильма:")
        await state.set_state(SearchState.waiting_for_movie_title)
    elif data == "movie_by_rating":
        await callback_query.message.answer("Введите диапазон рейтинга в формате: от-до (например, 7-9.5):")
        await state.set_state(SearchState.waiting_for_rating_range)
    elif data == "low_budget_movie":
        await search_and_send_movies(callback_query.message, search_low_budget_movies, limit=LIMIT, page=1, state=state)
    elif data == "high_budget_movie":
        await search_and_send_movies(callback_query.message, search_high_budget_movies, limit=LIMIT, page=1, state=state)
    elif data == "movie_by_year":
        await callback_query.message.answer("Введите год выпуска фильма (или диапазон в формате: от-до):")
        await state.set_state(SearchState.waiting_for_year)
    elif data == "movie_by_genre":
        await callback_query.message.answer(
            "Введите жанр фильма. Доступные жанры: Комедии, Мультфильмы, Ужасы, Фантастика, Триллеры, Боевики, Мелодрамы, "
            "Детективы, Приключения, Фэнтези, Военные, Семейные, Аниме, Исторические, Драмы, Документальные, Детские, "
            "Криминал, Биографии, Вестерны, Фильмы-нуар, Спортивные, Реальное ТВ, Короткометражки, Музыкальные, Мюзиклы, "
            "Ток-шоу, Игры."
        )
        await state.set_state(SearchState.waiting_for_genre)
    elif data == "history":
        await callback_query.message.answer("Введите дату для просмотра истории в формате ДД-ММ-ГГГГ:")
        await state.set_state(SearchState.waiting_for_history_date)
    elif data == "refresh":
        await refresh_search(callback_query.message, state)

async def show_main_menu(message: Message) -> None:
    """
    Отправляет сообщение с главной клавиатурой меню.
    
    Args:
        message (Message): Сообщение от пользователя.
    """
    await message.answer(
        "Выберите команду из меню ниже:",
        reply_markup=get_main_menu()
    )

@dp.message(Command(commands=['movie_search']))
async def movie_search(message: Message, state: FSMContext) -> None:
    
    await message.answer("Введите название фильма:")
    await state.set_state(SearchState.waiting_for_movie_title)

@dp.message(Command(commands=['movie_by_rating']))
async def rating_search_prompt(message: Message, state: FSMContext) -> None:
    
    await message.answer("Введите диапазон рейтинга в формате: от-до (например, 7-9.5):")
    await state.set_state(SearchState.waiting_for_rating_range)

async def search_and_send_movies(message: Message, search_function: Callable[..., Dict[str, Any]], **kwargs: Any) -> None:
    
    state = kwargs.pop('state', None)
    movies = search_function(**kwargs)

    if 'error' in movies:
        await message.answer(movies['error'])
    else:
        if movies.get('docs'):
            for movie in movies['docs']:
                movie_id = movie.get('id')
                title = movie.get('name')
                if not title:
                    continue

                movie_info = (
                    f"*Название:* {title}\n"
                    f"*Описание:* {movie.get('description', 'Нет описания')}\n"
                    f"*Рейтинг IMDb:* {movie.get('rating', {}).get('imdb', 'Нет рейтинга')}\n"
                    f"*Год:* {movie.get('year', 'Неизвестно')}\n"
                    f"*Жанр:* {', '.join([g['name'] for g in movie.get('genres', [])])}\n"
                    f"*Возрастной рейтинг:* {movie.get('ageRating', 'N/A')}\n"
                )
                poster_url = movie.get('poster', {}).get('url')

                if poster_url:
                    async with aiohttp.ClientSession() as session:
                        async with session.head(poster_url) as response:
                            if response.status == 200 and 'image' in response.headers.get('Content-Type', ''):
                                try:
                                    await bot.send_photo(message.chat.id, poster_url, caption="", parse_mode='Markdown')
                                except Exception as e:
                                    await message.answer(f"Ошибка при отправке изображения: {str(e)}")
                            else:
                                await message.answer("Не удалось загрузить изображение.")

                await message.answer(movie_info, parse_mode='Markdown')

                # Добавление информации о фильме в историю
                add_to_history({
                    "id": movie_id,
                    "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    "title": title,
                    "description": movie.get('description', 'Нет описания'),
                    "rating": movie.get('rating', {}).get('imdb', 'Нет рейтинга'),
                    "year": movie.get('year', 'Неизвестно'),
                    "genre": ', '.join([g['name'] for g in movie.get('genres', [])]),
                    "age_rating": movie.get('ageRating', 'N/A'),
                    "poster": poster_url,
                    "watched": False
                })

            if state:
                await state.update_data(search_function=search_function, kwargs=kwargs)
            await message.answer("Чтобы обновить результаты, нажмите кнопку 'Обновить'.")
        else:
            await message.answer("По вашему запросу фильмов не найдено.")
        await show_main_menu(message)

@dp.message(Command(commands=['low_budget_movie']))
async def low_budget_movie_search(message: Message, state: FSMContext) -> None:
    
    await search_and_send_movies(message, search_low_budget_movies, limit=LIMIT, page=1, state=state)

@dp.message(Command(commands=['high_budget_movie']))
async def high_budget_movie_search(message: Message, state: FSMContext) -> None:
    
    await search_and_send_movies(message, search_high_budget_movies, limit=LIMIT, page=1, state=state)

@dp.message(Command(commands=['movie_by_year']))
async def movie_by_year_prompt(message: Message, state: FSMContext) -> None:
   
    await message.answer("Введите год выпуска фильма (или диапазон в формате: от-до):")
    await state.set_state(SearchState.waiting_for_year)

@dp.message(Command(commands=['movie_by_genre']))
async def movie_by_genre_prompt(message: Message, state: FSMContext) -> None:
    
    await message.answer("Введите жанр фильма. Доступные жанры: Комедии, Мультфильмы, Ужасы, Фантастика, Триллеры, Боевики, "
                         "Мелодрамы, Детективы, Приключения, Фэнтези, Военные, Семейные, Аниме, Исторические, Драмы, "
                         "Документальные, Детские, Криминал, Биографии, Вестерны, Фильмы-нуар, Спортивные, Реальное ТВ, "
                         "Короткометражки, Музыкальные, Мюзиклы, Ток-шоу, Игры.")
    await state.set_state(SearchState.waiting_for_genre)

@dp.callback_query(lambda c: c.data.startswith("mark_"))
async def mark_movie_status(callback_query: CallbackQuery) -> None:
   
    data = callback_query.data
    parts = data.split("_", 2)

    action = f"{parts[0]}_{parts[1]}"
    movie_id = parts[2]

    if action == "mark_watched":
        mark_movie_as_watched(movie_id, True)
    elif action == "mark_not_watched":
        mark_movie_as_watched(movie_id, False)
    await callback_query.message.edit_reply_markup()  # Убираем клавиатуру после обработки

def get_watch_buttons(movie_id: str) -> InlineKeyboardMarkup:
    
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Просмотрен", callback_data=f"mark_watched_{movie_id}"),
            InlineKeyboardButton(text="Не просмотрен", callback_data=f"mark_not_watched_{movie_id}")
        ]
    ])
    return buttons

def parse_date(date_str: str) -> Optional[str]:
    
    try:
        parsed_date = datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        try:
            parsed_date = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            try:
                parsed_date = datetime.strptime(date_str, "%d.%m.%y")
                parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
            except ValueError:
                return None
    return parsed_date.strftime("%d-%m-%Y")

@dp.message(SearchState.waiting_for_history_date)
async def show_history_for_date(message: Message, state: FSMContext) -> None:
    """
    Показывает историю запросов за указанную дату.
    
    Args:
        message (Message): Сообщение от пользователя.
        state (FSMContext): Контекст состояния машины состояний.
    """
    date_str = message.text.strip()
    formatted_date = parse_date(date_str)
    
    if formatted_date:
        history = get_history_by_date(formatted_date)
        if history:
            for entry in history:
                movie_info = (
                    f"*Дата поиска:* {entry['date']}\n"
                    f"*Название:* {entry['title']}\n"
                    f"*Описание:* {entry['description'] or 'Нет описания'}\n"
                    f"*Рейтинг:* {entry['rating']}\n"
                    f"*Год производства:* {entry['year']}\n"
                    f"*Жанр:* {entry['genre']}\n"
                    f"*Возрастной рейтинг:* {entry['age_rating']}\n"
                    f"*Статус:* {'Просмотрен' if entry.get('watched', False) else 'Не просмотрен'}\n"
                )
                await message.answer(movie_info, parse_mode='Markdown')

                # Отправка постера, если он есть
                if entry.get('poster'):
                    await bot.send_photo(message.chat.id, entry['poster'])

                # Кнопки для отмечания как просмотренного или непросмотренного
                markup = get_watch_buttons(entry['id'])
                await message.answer("Отметьте статус фильма:", reply_markup=markup)

            await message.answer("Вы можете отметить фильмы как просмотренные или непросмотренные.", reply_markup=get_main_menu())
        else:
            await message.answer("История за указанную дату не найдена.")
    else:
        await message.answer("Некорректный формат даты. Используйте ДД-ММ-ГГГГ, Д.ММ.ГГГГ или Д.ММ.ГГ.")

    await state.clear()

@dp.message(Command(commands=['history']))
async def request_history_date(message: Message, state: FSMContext) -> None:
   
    await message.answer("Введите дату для просмотра истории в формате ГГГГ-ММ-ДД:")
    await state.set_state(SearchState.waiting_for_history_date)

@dp.message()
async def handle_message(message: Message, state: FSMContext) -> None:
    
    current_state = await state.get_state()
    text = message.text.strip()

    if current_state == SearchState.waiting_for_movie_title.state:
        await search_and_send_movies(message, search_movies, title=text, limit=LIMIT, page=1, state=state)

    elif current_state == SearchState.waiting_for_rating_range.state:
        try:
            rating_start, rating_end = map(float, text.split('-'))
            if 0 <= rating_start <= 10 and 0 <= rating_end <= 10:
                await search_and_send_movies(message, movie_by_rating, rating_from=rating_start, rating_to=rating_end, limit=LIMIT, page=1, state=state)
            else:
                await message.answer("Рейтинг должен быть в диапазоне от 0 до 10.")
        except ValueError:
            await message.answer("Пожалуйста, введите корректный диапазон рейтинга в формате: от-до.")

    elif current_state == SearchState.waiting_for_year.state:
        try:
            year_range = text.split('-')
            if len(year_range) == 1:
                year = int(year_range[0])
                if 1930 <= year <= 2024:
                    await search_and_send_movies(message, search_movies_by_year, year_start=year, year_end=year, limit=LIMIT, page=1, state=state)
                else:
                    await message.answer("Год должен быть в диапазоне от 1930 до 2024.")
            elif len(year_range) == 2:
                year_start, year_end = map(int, year_range)
                if 1930 <= year_start <= 2024 and 1930 <= year_end <= 2024:
                    await search_and_send_movies(message, search_movies_by_year, year_start=year_start, year_end=year_end, limit=LIMIT, page=1, state=state)
                else:
                    await message.answer("Годы должны быть в диапазоне от 1930 до 2024.")
            else:
                await message.answer("Пожалуйста, введите год или диапазон годов в формате: от-до.")
        except ValueError:
            await message.answer("Пожалуйста, введите корректный диапазон годов в формате: от-до.")

    elif current_state == SearchState.waiting_for_genre.state:
        genre = text.strip()
        await search_and_send_movies(message, search_movies_by_genre, genre=genre, limit=LIMIT, page=1, state=state)

async def refresh_search(message: Message, state: FSMContext) -> None:
   
    data = await state.get_data()
    search_function = data.get('search_function')
    kwargs = data.get('kwargs', {})
    page = kwargs.get('page', 1) + 1
    kwargs['page'] = page

    if search_function:
        try:
            await search_and_send_movies(message, search_function, **kwargs, state=state)
        except KeyError:
            await message.answer("Ошибка при обновлении запроса. Попробуйте снова.")
    else:
        await message.answer("Нет предыдущего запроса для обновления.")

async def main() -> None:
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
