from bs4 import BeautifulSoup
from selenium import webdriver
from utils.models import Manga
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service

class Mangareader(Manga):
    domain = 'mangareader.mobi'

    def get_chapters(manga):
        response = Mangareader.send_request(f'https://mangareader.mobi/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('div', {'class':'cl'}).find_all('a')
        chapters = [div['href'].split('/')[-1] for div in divs[::-1]]
        chapters = [chapter.replace(f'{manga}-','') for chapter in chapters]
        return chapters

    def get_images(manga, chapter):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://mangareader.mobi/chapter/{manga}-{chapter}')
        select = Select(browser.find_element(By.XPATH, '//select[@class="loadImgType pull-left"]'))
        select.select_by_value('1')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        images = soup.find('div', {'class': 'comic_wraCon text-center'}).find_all('img')
        images = [image['src'] for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        from contextlib import suppress
        page = 1
        while True:
            try:
                response = Mangareader.send_request(f'https://mangareader.mobi/search?s={keyword}&page={page}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find('div', {'id': 'content'}).find('ul').find_all('li')
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'left'}).find('a')
                if absolute and keyword.lower() not in ti.text.lower():
                    continue
                latest_chapter, genres, status = '', '', ''
                contents = manga.find('div', {'class': 'info'}).findChildren('span', recursive=False)
                for content in contents:
                    if content.has_attr('class'):
                        genres_list = [genre.text.strip() for genre in content.find_all('a')]
                        genres = ', '.join(genres_list)
                    elif content.find('b'):
                        status = content.text.replace('Status: ', '').strip()
                    else:
                        with suppress(Exception): latest_chapter = content.find('a')['href'].split('/')[-1]
                results[ti.text.strip()] = {
                    'domain': Mangareader.domain,
                    'url': ti['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'genres': genres,
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Mangareader.search_by_keyword('', False)

    def send_request(url):
        import requests, warnings
        from urllib3.exceptions import InsecureRequestWarning
        from utils.assets import waiter
        def warn(*args, **kwargs):
            if args[1] is InsecureRequestWarning:
                pass
        warnings.warn = warn
        while True:
            try:
                response = requests.get(url, verify=False)
                response.raise_for_status()
                return response
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                waiter()