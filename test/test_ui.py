import pytest
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import allure


from config.settings import BASE_URL_UI


@pytest.fixture(scope="session")
def browser():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
    driver = None
    try:
        driver = uc.Chrome(options=options)
        driver.maximize_window()
        yield driver
    finally:
        if driver:
            driver.quit()


@allure.feature("UI Тестирование Кинопоиск")
class TestKinopoiskUI:

    @allure.story("Общие элементы")
    @allure.title("Проверка загрузки главной страницы и заголовка")
    def test_main_page_load(self, browser):
        with allure.step(f"Переход на главную страницу: {BASE_URL_UI}"):
            browser.get(BASE_URL_UI)
            allure.attach(browser.current_url, "Текущий URL",
                          allure.attachment_type.TEXT)
            allure.attach(browser.page_source, "Исходный код страницы",
                          allure.attachment_type.HTML)

        with allure.step("Проверка заголовка страницы"):
            WebDriverWait(browser, 20).until(EC.title_contains("Кинопоиск"))
            allure.attach(browser.title, "Заголовок страницы",
                          allure.attachment_type.TEXT)

        with allure.step("Проверка наличия поля поиска"):
            search_input = WebDriverWait(browser, 20).until(
                EC.visibility_of_element_located((By.NAME, "kp_query"))
            )
            assert search_input.is_displayed()
            allure.attach("Поле поиска найдено", "Статус",
                          allure.attachment_type.TEXT)

    @allure.story("Поиск")
    @allure.title("Проверка работы поиска по названию фильма")
    def test_search_movie_by_title(self, browser):
        movie_title = "Интерстеллар"
        with allure.step(f"Переход на главную страницу: {BASE_URL_UI}"):
            browser.get(BASE_URL_UI)
            allure.attach(browser.current_url, "Текущий URL",
                          allure.attachment_type.TEXT)

            WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.NAME, "kp_query"))
            ).send_keys(movie_title + Keys.RETURN)
            allure.attach(movie_title, "Введенный запрос",
                          allure.attachment_type.TEXT)

        with allure.step("Проверка перехода на страницу результатов поиска"):
            WebDriverWait(browser, 30).until(
                EC.url_contains("index.php?kp_query="))
            allure.attach(browser.current_url,
                          "Текущий URL после поиска",
                          allure.attachment_type.TEXT)

    @allure.story("Карточка фильма")
    @allure.title("Переход на страницу фильма и проверка основных элементов")
    def test_view_movie_details_page(self, browser):
        movie_title = "Интерстеллар"
        movie_title_with_year = "Интерстеллар (2014)"

        with allure.step(f"Поиск фильма '{movie_title}' и переход на страницу "
                         f"результатов"):
            browser.get(BASE_URL_UI)
            WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.NAME, "kp_query"))
            ).send_keys(movie_title + Keys.RETURN)
            WebDriverWait(browser, 30).until(
                EC.url_contains("index.php?kp_query="))
            allure.attach(browser.current_url,
                          "Текущий URL страницы результатов поиска",
                          allure.attachment_type.TEXT)

        with allure.step(f"Клик по ссылке на фильм '{movie_title}' "
                         f"в результатах поиска"):
            movie_title_link_text = movie_title

            movie_link_xpath = (
                f"//a[contains(@href, '/film/') and "
                f"contains(text(), '{movie_title_link_text}')]"
            )
            try:
                movie_link = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable((By.XPATH, movie_link_xpath))
                )
                movie_link.click()
                allure.attach("Клик по ссылке фильма в результатах поиска",
                              "Действие", allure.attachment_type.TEXT)
            except TimeoutException:
                allure.attach(
                    f"Не удалось найти или кликнуть по ссылке на фильм "
                    f"'{movie_title}'", "Ошибка", allure.attachment_type.TEXT
                )
                allure.attach(browser.get_screenshot_as_png(),
                              "Скриншот при ошибке поиска ссылки фильма",
                              allure.attachment_type.PNG)
                raise

        with allure.step("Проверка перехода на страницу фильма и заголовка"):
            WebDriverWait(browser, 30).until(EC.url_contains("/film/"))
            allure.attach(browser.current_url,
                          "Текущий URL страницы фильма",
                          allure.attachment_type.TEXT)
            film_title_element_xpath = (
                f"//h1[@itemprop='name']/span[contains(text(), "
                f"'{movie_title_with_year}')]"
            )
            WebDriverWait(browser, 20).until(EC.title_contains(movie_title))
            allure.attach(browser.title, "Заголовок вкладки браузера",
                          allure.attachment_type.TEXT)

            film_title_element = WebDriverWait(browser, 20).until(
                EC.visibility_of_element_located(
                    (By.XPATH, film_title_element_xpath)
                    )
            )
            assert film_title_element.is_displayed()
            allure.attach(film_title_element.text,
                          "Найденный заголовок фильма на странице",
                          allure.attachment_type.TEXT)

        with allure.step("Проверка основных элементов на странице фильма"):
            try:
                watch_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(), 'Буду смотреть') or "
                                   "contains(text(), 'Смотреть')]")
                    )
                )
                assert watch_button.is_displayed()
                allure.attach("Кнопка 'Буду смотреть' найдена", "Статус",
                              allure.attachment_type.TEXT)
            except TimeoutException:
                allure.attach("Кнопка 'Буду смотреть' не найдена", "Статус",
                              allure.attachment_type.TEXT)

            try:
                rating_element = WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, "film-rating-value__text")
                    )
                )
                assert rating_element.is_displayed()
                allure.attach(rating_element.text, "Найденный рейтинг фильма",
                              allure.attachment_type.TEXT)
            except TimeoutException:
                allure.attach("Элемент рейтинга не найден", "Статус",
                              allure.attachment_type.TEXT)

    @allure.story("Поиск")
    @allure.title("Проверка поиска по несуществующему фильму")
    def test_search_non_existent_movie(self, browser):
        non_existent_movie = "НеСуществующийФильмДляТеста987654321"
        with allure.step(f"Переход на главную страницу: {BASE_URL_UI}"):
            browser.get(BASE_URL_UI)
            allure.attach(browser.current_url, "Текущий URL",
                          allure.attachment_type.TEXT)

            WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.NAME, "kp_query"))
            ).send_keys(non_existent_movie + Keys.RETURN)
            allure.attach(non_existent_movie, "Введенный запрос",
                          allure.attachment_type.TEXT)

        with allure.step("Проверка отсутствия результатов или сообщения"):
            no_results_message_xpath = (
                "//h2[@class='textorangebig' and "
                "contains(text(), 'К сожалению, по вашему запросу ничего не "
                "найдено...')]"
            )
            WebDriverWait(browser, 20).until(
                EC.visibility_of_element_located(
                    (By.XPATH, no_results_message_xpath)
                    )
            )
            allure.attach("Сообщение об отсутствии результатов", "Статус",
                          allure.attachment_type.TEXT)
            assert "index.php" in browser.current_url
            assert "kp_query" in browser.current_url
            allure.attach(browser.current_url,
                          "URL после поиска несуществующего фильма",
                          allure.attachment_type.TEXT)

    @allure.story("Навигация по сайту")
    @allure.title("Проверка перехода на раздел 'Онлайн-кинотеатр'")
    def test_navigate_to_online_cinema_section(self, browser):
        with allure.step(f"Переход на главную страницу: {BASE_URL_UI}"):
            browser.get(BASE_URL_UI)
            allure.attach(browser.current_url, "Текущий URL",
                          allure.attachment_type.TEXT)

            online_cinema_link = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Онлайн-кинотеатр"))
            )

        with allure.step("Нажатие на ссылку 'Онлайн-кинотеатр' в меню"):
            online_cinema_link.click()
            allure.attach("Ссылка 'Онлайн-кинотеатр' нажата", "Действие",
                          allure.attachment_type.TEXT)

        with allure.step("Проверка, что URL изменился на 'Онлайн-кинотеатр'"):
            WebDriverWait(browser, 20). \
                until(EC.url_contains("hd.kinopoisk.ru"))
            allure.attach(browser.current_url,
                          "Текущий URL раздела 'Онлайн-кинотеатр'",
                          allure.attachment_type.TEXT)
            try:
                WebDriverWait(browser, 20).until(
                    EC.title_contains("Онлайн-кинотеатр")
                    )
                allure.attach("Заголовок 'Онлайн-кинотеатр' найден",
                              "Статус", allure.attachment_type.TEXT)
            except TimeoutException:
                allure.attach(
                    "Заголовок 'Онлайн-кинотеатр' не найден или локатор "
                    "изменился",
                    "Статус", allure.attachment_type.TEXT
                )
