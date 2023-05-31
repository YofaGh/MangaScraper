from bs4 import BeautifulSoup
from utils.models import Manga
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

class Manga18(Manga):
    domain = 'manga18.club'

    def get_chapters(manga):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://manga18.club/manhwa/{manga}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        lis = soup.find('div', {'class': 'chapter_box'}).find_all('li')
        chapters = [li.find('a')['href'].split('/')[-1] for li in lis[::-1]]
        return chapters

    def get_images(manga, chapter):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://manga18.club/manhwa/{manga}/{chapter}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        images = soup.find('div', {'class':'chapter_boxImages'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        page = 1
        while True:
            browser.get(f'https://manga18.club/list-manga/{page}?search={keyword}')
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            mangas = soup.find_all('div', {'class': 'col-md-3 col-sm-4 col-xs-6'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'mg_name'}).find('a')
                if absolute and keyword.lower() not in ti.contents[0].lower():
                    continue
                latest_chapter = ''
                with suppress(Exception): latest_chapter = manga.find('div', {'class': 'mg_chapter'}).find('a')['href'].split('/')[-1]
                results[ti.contents[0]] = {
                    'domain': Manga18.domain,
                    'url': ti['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manga18.search_by_keyword('', False)