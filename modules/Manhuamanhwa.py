from utils.Bases import Manga, Req
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class Manhuamanhwa(Manga, Req):
    def get_chapters(manga):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://manhuamanhwa.com/manga/{manga}/')
        WebDriverWait(browser, 60).until(ec.presence_of_element_located((By.XPATH, '//li[@class="wp-manga-chapter    "]')))
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manhuamanhwa.send_request(f'https://manhuamanhwa.com/manga/{manga}/{chapter}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['data-src'] for image in images]
        return images, False

    def search(title, absolute=False):
        import time
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://manhuamanhwa.com/?s={title}&post_type=wp-manga')
        found = []
        while True:
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            mangas = soup.find_all('div', {'class': 'post-title'})
            results = []
            for manga in mangas:
                di = manga.find('a')
                if absolute and title.lower() not in di.contents[0].lower():
                    continue
                if manga not in found:
                    found.append(manga)
                    results.append(f'title: {di.contents[0]}, url: {di["href"].split("/")[-2]}')
            yield results
            try:
                load_more_button = browser.find_element(By.XPATH, "//div[@class='load-title']")
                load_more_button.click()
                time.sleep(1)
            except:
                yield []