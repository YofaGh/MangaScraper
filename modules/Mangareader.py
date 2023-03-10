from utils.Bases import Manga, Req
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

class Mangareader(Manga, Req):
    def get_chapters(manga):
        response = Mangareader.send_request(f'https://mangareader.cc/manga/{manga}')
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
        browser.get(f'https://mangareader.cc/chapter/{manga}-{chapter}')
        select = Select(browser.find_element(By.XPATH, '//select[@class="loadImgType pull-left"]'))
        select.select_by_value('1')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        images = soup.find('div', {'class': 'comic_wraCon text-center'}).find_all('img')
        images = [image['src'] for image in images]
        return images, False

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = Mangareader.send_request(f'https://mangareader.cc/search?s={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'anipost'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                results[manga.find('a')['href'].split('/')[-1]] = manga.find('a').find('h3').contents[0]
            page += 1
        yield results
        return