import time
from utils.Bases import Doujin, Req
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

class Hentaifox(Doujin, Req):
    def get_title(code):
        response = Hentaifox.send_request(f'https://hentaifox.com/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'info'}).find('h1').contents[0]
        return title

    def get_images(code):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://hentaifox.com/gallery/{code}/')
        time.sleep(5)
        view_all_button = browser.find_element(By.XPATH, "//button[@id='load_all']")
        view_all_button.click()
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        divs = soup.find_all('div', {'class': 'gallery_thumb'})
        for _ in range(21):
            if len(divs) != 10:
                break
            time.sleep(1)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            divs = soup.find_all('div', {'class': 'gallery_thumb'})
        images = [div.find('img')['data-src'] for div in divs]
        new_images = []
        for image in images:
            name = image.rsplit('/', 1)[1]
            name = name.replace('t.', '.')
            new_images.append(f'{image.rsplit("/", 1)[0]}/{name}')
        return new_images

    def search(title, absolute):
        page = 1
        while True:
            response = Hentaifox.send_request(f'https://hentaifox.com/search/?q={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'caption'})
            if len(doujins) == 0:
                yield []
            results = []
            for doujin in doujins:
                if absolute and title.lower() not in doujin.find('a').contents[0].lower():
                    continue
                results.append(f'title: {doujin.find("a").contents[0]}, code: {doujin.find("a")["href"].split("/")[-2]}')
            yield results
            page += 1