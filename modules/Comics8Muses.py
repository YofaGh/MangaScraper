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

    def search(title, sleep_time, absolute=False, limit_page=1000):
        import time
        results = []
        page = 1
        links = []
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        while page <= limit_page:
            yield False, page
            browser.get(f'https://comics.8muses.com/search?q={title}&page={page}')
            time.sleep(2)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            comics = soup.find_all('a', {'class': 'c-tile t-hover'}, href=True)
            if not comics:
                break
            for comic in comics:
                if not comic.get('href'):
                    continue
                if absolute and title.lower() not in comic.find('span').contents[0].lower():
                    continue
                url = comic.get('href').replace('https://comics.8muses.com/comics/album/', '')
                sublink = False
                for link in links:
                    if link in url:
                        sublink = True
                        break
                if not sublink:
                    links.append(url)
                    results.append(f'title: {comic.find("span").contents[0]}, url:{url}') 
            page += 1
            time.sleep(sleep_time)
        yield True, results
        return

    def rename_chapter(name):
        return name.replace('-', ' ')