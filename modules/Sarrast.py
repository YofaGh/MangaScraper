from bs4 import BeautifulSoup
from utils.models import Manga
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

class Sarrast(Manga):
    domain = 'sarrast.com'

    def get_chapters(manga):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://sarrast.com/series/{manga}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        divs = soup.find('div', {'class': 'text-white mb-20 mt-8 relative px-4'}).find_all('a')
        chapters = [div['href'].split('/')[-1] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://sarrast.com/series/{manga}/{chapter}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        images = soup.find('div', {'class': 'episode w-full flex flex-col items-center'}).find_all('img')
        images = [f'https://sarrast.com{image["src"]}' for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        import json
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        try:
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
            service = Service(executable_path='geckodriver.exe', log_path='NUL')
            browser = webdriver.Firefox(options=options, service=service)
            browser.get(f'https://sarrast.com/search?value={keyword}')
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            mangas = soup.find('div', {'id': 'json'}).contents[0]
            mangas = json.loads(mangas)
            results = {}
            for manga in mangas:
                results[manga['title']] = {
                    'domain': Sarrast.domain,
                    'url': manga['slug'],
                }
            yield results
        except HTTPError:
            yield {}
        except Timeout as error:
            raise error
        except RequestException:
            waiter()
        yield {}

    def get_db():
        return Sarrast.search_by_keyword('', False)