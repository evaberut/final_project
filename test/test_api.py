import pytest  # noqa: F401
import allure
import requests
import json

from config.settings import BASE_URL_API, KINOPOISK_API_KEY


def attach_json(data, name):
    allure.attach(json.dumps(data, indent=2),
                  name, allure.attachment_type.JSON)


@allure.feature("API Тесты Неофициального Кинопоиска")
class TestKinopoiskAPI:

    @allure.story("Поиск фильмов")
    @allure.title("Поиск существующего фильма по названию")
    def test_search_movie_success(self):
        query = "Интерстеллар"
        url = f"{BASE_URL_API}/movie/search"
        headers = {
            "accept": "application/json",
            "X-API-KEY": KINOPOISK_API_KEY
        }
        params = {
            "query": query
        }

        with allure.step(f"Отправка GET-запроса на поиск фильма: {url} "
                         f"с параметрами: {params}"):
            response = requests.get(url, headers=headers, params=params)
            allure.attach(f"Response URL: {response.url}",
                          "Request URL", allure.attachment_type.TEXT)
            allure.attach(f"Status Code: {response.status_code}",
                          "Response Status Code", allure.attachment_type.TEXT)
            attach_json(response.json(), "Response JSON")

        with allure.step("Проверка статус-кода ответа: 200"):
            assert response.status_code == 200, (
                f"Ожидался статус 200, получен {response.status_code}"
            )

        with allure.step("Проверка наличия результатов и соответствия"):
            data = response.json()
            assert "docs" in data, "В ответе нет 'docs' (список фильмов)"
            assert isinstance(data["docs"], list), "'docs' должен быть списком"
            assert len(data["docs"]) > 0, "Список результатов пуст"
            found = False
            for movie in data["docs"]:
                if query.lower() in movie.get("name", "").lower():
                    found = True
                    break
            assert found, f"Фильм '{query}' не найден в результатах поиска"

    @allure.story("Поиск фильмов")
    @allure.title("Поиск несуществующего фильма по названию")
    def test_search_movie_not_found(self):
        query = "НеСуществующийФильмДляТеста987654321"
        url = f"{BASE_URL_API}/movie/search"
        headers = {
            "accept": "application/json",
            "X-API-KEY": KINOPOISK_API_KEY
        }
        params = {
            "query": query
        }

        with allure.step(f"GET-запрос на несуществующий фильм: {url} "
                         f"с параметрами: {params}"):
            response = requests.get(url, headers=headers, params=params)
            allure.attach(f"Response URL: {response.url}",
                          "Request URL", allure.attachment_type.TEXT)
            allure.attach(f"Status Code: {response.status_code}",
                          "Response Status Code", allure.attachment_type.TEXT)
            attach_json(response.json(), "Response JSON")

        with allure.step("Проверка статус-кода ответа: 200"):
            assert response.status_code == 200, (
                f"Ожидался статус 200, получен {response.status_code}"
            )

        with allure.step("Проверка, что список результатов пуст"):
            data = response.json()
            assert "docs" in data, "В ответе отсутствуют 'docs'"
            assert isinstance(data["docs"], list), "'docs' должен быть списком"
            assert len(data["docs"]) == 0, (
                "Список результатов не пуст для несуществующего фильма"
            )

    @allure.story("Информация о фильме")
    @allure.title("Получение деталей фильма по ID")
    def test_get_movie_details_by_id(self):
        movie_id = 258687
        url = f"{BASE_URL_API}/movie/{movie_id}"
        headers = {
            "accept": "application/json",
            "X-API-KEY": KINOPOISK_API_KEY
        }

        with allure.step(f"Отправка GET-запроса на получение деталей фильма "
                         f"ID={movie_id}: {url}"):
            response = requests.get(url, headers=headers)
            allure.attach(f"Response URL: {response.url}",
                          "Request URL", allure.attachment_type.TEXT)
            allure.attach(f"Status Code: {response.status_code}",
                          "Response Status Code", allure.attachment_type.TEXT)
            attach_json(response.json(), "Response JSON")

        with allure.step("Проверка статус-кода ответа: 200"):
            assert response.status_code == 200, (
                f"Ожидался статус 200, получен {response.status_code}"
            )

        with allure.step("Проверка, что название соответствует ожидаемому"):
            data = response.json()
            expected_title = "Интерстеллар"
            assert data.get("name") == expected_title, (
                f"Ожидаемое название '{expected_title}', "
                f"получено '{data.get('name')}'"
            )
            assert "description" in data, "В ответе нет описания фильма"
            assert data.get("year") == 2014, "Неверный год выпуска фильма"

    @allure.story("Обработка ошибок API")
    @allure.title("Проверка запроса с невалидным API ключом")
    def test_invalid_api_key_error(self):
        url = f"{BASE_URL_API}/movie/random"
        headers = {
            "accept": "application/json",
            "X-API-KEY": "INVALID_API_KEY"
        }
        with allure.step(f"GET-запрос с невалидным API ключом к {url}"):
            response = requests.get(url, headers=headers)
            allure.attach(f"Response URL: {response.url}",
                          "Request URL", allure.attachment_type.TEXT)
            allure.attach(f"Status Code: {response.status_code}",
                          "Response Status Code", allure.attachment_type.TEXT)
            attach_json(response.json(), "Response JSON")

        with allure.step("Проверка статус-кода ответа: 401/403"):
            assert response.status_code in [401, 403], (
                f"Ожидался статус 401 или 403, получен {response.status_code}"
            )

        with allure.step("Проверка сообщения об ошибке (если есть)"):
            data = response.json()
            assert any(msg in data.get("message", "").lower()
                       for msg in ["invalid api key", "unauthorized",
                                   "forbidden",
                                   "переданный токен некорректен!"]), (
                f"Ожидаемое сообщение об ошибке не найдено. "
                f"Получено: {data}"
            )

    @allure.story("Информация о фильме")
    @allure.title("Получение деталей фильма по несуществующему ID")
    def test_get_movie_details_non_existent_id(self):
        non_existent_movie_id = 100
        url = f"{BASE_URL_API}/movie/{non_existent_movie_id}"
        headers = {
            "accept": "application/json",
            "X-API-KEY": KINOPOISK_API_KEY
        }

        with allure.step(f"Отправка GET-запроса на получение деталей фильма с "
                         f"несуществующим ID={non_existent_movie_id}: {url}"):
            response = requests.get(url, headers=headers)
            allure.attach(f"Response URL: {response.url}",
                          "Request URL", allure.attachment_type.TEXT)
            allure.attach(f"Status Code: {response.status_code}",
                          "Response Status Code", allure.attachment_type.TEXT)
            attach_json(response.json(), "Response JSON")

        with allure.step("Проверка статус-кода ответа: 400"):
            assert response.status_code == 400, (
                f"Ожидался статус 400, получен {response.status_code}"
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()
            assert "message" in data, "В ответе нет сообщения об ошибке"
            expected_error_message_part = (
                "Значение поля id должно быть в диапазоне от 250 до 10000000!"
            )
            actual_messages = data.get("message", [])
            assert any(expected_error_message_part in msg
                       for msg in actual_messages), (
                f"Неверное сообщение об ошибке. "
                f"Ожидалось: '{expected_error_message_part}', "
                f"Получено: {actual_messages}"
            )

    @allure.story("Фильтры и списки")
    @allure.title("Получение списка фильмов по жанру 'комедия'")
    def test_get_movies_by_genre(self):
        genre = "комедия"
        url = f"{BASE_URL_API}/movie"
        headers = {
            "accept": "application/json",
            "X-API-KEY": KINOPOISK_API_KEY
        }
        params = {
            "genres.name": genre,
            "limit": 10
        }

        with allure.step(f"GET-запрос на получение по жанру '{genre}': "
                         f"{url} с параметрами: {params}"):
            response = requests.get(url, headers=headers, params=params)
            allure.attach(f"Response URL: {response.url}",
                          "Request URL", allure.attachment_type.TEXT)
            allure.attach(f"Status Code: {response.status_code}",
                          "Response Status Code", allure.attachment_type.TEXT)
            attach_json(response.json(), "Response JSON")

        with allure.step("Проверка статус-кода ответа: 200"):
            assert response.status_code == 200, (
                f"Ожидался статус 200, получен {response.status_code}"
            )

        with allure.step("Проверка наличия фильмов и соответствия жанру"):
            data = response.json()
            assert "docs" in data, "В ответе отсутствуют 'docs'"
            assert isinstance(data["docs"], list), "'docs' должен быть списком"
            assert len(data["docs"]) > 0, "Список фильмов по жанру пуст"

            found_genre_match = False
            for movie in data["docs"]:
                genres = [g["name"].lower() for g in movie.get("genres", [])]
                if genre.lower() in genres:
                    found_genre_match = True
                    break
            assert found_genre_match, (
                f"В полученном списке нет фильмов с жанром '{genre}'"
            )
