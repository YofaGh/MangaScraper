import time
from utils.models import Doujin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

class Hentaifox(Doujin):
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

    def search_by_keyword(keyword, absolute):
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Hentaifox.send_request(f'https://hentaifox.com/search/?q={keyword}&page={page}')
                soup = BeautifulSoup(response.text, 'html.parser')
                doujins = soup.find_all('div', {'class': 'thumb'})
                if len(doujins) == 0:
                    yield {}
                results = {}
                for doujin in doujins:
                    caption = doujin.find('div', {'class': 'caption'})
                    ti = caption.find('a').contents[0]
                    if absolute and keyword.lower() not in ti.lower():
                        continue
                    results[ti] = {
                        'domain': 'hentaifox.com',
                        'code': caption.find('a')['href'].split('/')[-2],
                        'category': doujin.find('a', {'class':'t_cat'}).contents[0],
                        'page': page
                    }
                yield results
                page += 1
            except HTTPError:
                yield {}
            except Timeout as error:
                raise error
            except RequestException:
                waiter()

    def get_db():
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        response = Hentaifox.send_request('https://hentaifox.com/categories/')
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.find('div', {'class': 'list_tags'}).find_all('a')
        categories = [a['href'] for a in categories]
        for category in categories:
            page = 1
            while True:
                try:
                    response = Hentaifox.send_request(f'https://hentaifox.com{category}pag/{page}/')
                    soup = BeautifulSoup(response.text, 'html.parser')
                    doujins = soup.find_all('div', {'class': 'thumb'})
                    if len(doujins) == 0:
                        break
                    results = {}
                    for doujin in doujins:
                        caption = doujin.find('div', {'class': 'caption'})
                        ti = caption.find('a').contents[0]
                        results[ti] = {
                            'domain': 'hentaifox.com',
                            'code': caption.find('a')['href'].split('/')[-2],
                            'category': doujin.find('a', {'class':'t_cat'}).contents[0]
                        }
                    yield results
                    page += 1
                except HTTPError:
                    break
                except Timeout as error:
                    raise error
                except RequestException:
                    waiter()
        yield {}