from utils.Bases import Manga, Req
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

class Comics8Muses(Manga, Req):
    def get_chapters(manga):
        page = 1
        chapters = []
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://comics.8muses.com/comics/album/{manga}/{page}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        if not soup.find('div', {'class':'image-title'}):
            return ['']
        while True:
            links = soup.find_all('a', {'class': 'c-tile t-hover'}, href=True)
            if not links:
                break
            chapters += [link.get('href').split('/')[-1] for link in links]
            page += 1
            browser.get(f'https://comics.8muses.com/comics/album/{manga}/{page}')
            soup = BeautifulSoup(browser.page_source, 'html.parser')
        return chapters

    def get_images(manga, chapter):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://comics.8muses.com/comics/album/{manga}/{chapter}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        links = soup.find_all('a', {'class': 'c-tile t-hover'})
        images = [link.find('img').get('data-src') for link in links]
        images = [f'https://comics.8muses.com/image/fm/{image.split("/")[-1]}' for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        links = []
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        while True:
            yield page
            if page > limit_page:
                break
            browser.get(f'https://comics.8muses.com/search?q={title}&page={page}')
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            comics = soup.find_all('a', {'class': 'c-tile t-hover'}, href=True)
            if not comics:
                break
            for comic in comics:
                if not comic.get('href'):
                    continue
                url = comic.get('href').replace('https://comics.8muses.com/comics/album/', '')
                sublink = False
                for link in links:
                    if link in url:
                        sublink = True
                        break
                if not sublink:
                    links.append(url)
                    results[url] = comic.find('span').contents[0]
            page += 1
        yield results
        return

    def rename_chapter(name):
        return name.replace('-', ' ')