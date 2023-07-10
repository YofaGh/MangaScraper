from bs4 import BeautifulSoup
from utils.models import Doujin

class Myreadingmanga(Doujin):
    domain = 'myreadingmanga.to'

    def get_title(code):
        response = Myreadingmanga.send_request(f'https://myreadingmanga.to/g/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'container'}).find('h1').text
        return title

    def get_images(code):
        response = Myreadingmanga.send_request(f'https://myreadingmanga.to/g/{code}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('a', {'class': 'gallerythumb'})
        images = [div.find('img')['data-src'] for div in divs]
        new_images = []
        for image in images:
            name = image.rsplit('/', 1)[1]
            name = name.replace('t.', '.')
            new_images.append(f'{image.rsplit("/", 1)[0]}/{name}')
        return new_images

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Myreadingmanga.send_request(f'https://myreadingmanga.to/search?q={keyword}&page={page}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'gallery'})
            if len(doujins) == 0:
                yield {}
            results = {}
            for doujin in doujins:
                doj = doujin.find('a')
                ti = doj.find('div', {'class': 'caption'}).contents[0]
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    'domain': Myreadingmanga.domain,
                    'code': doj['href'].split('/')[-2],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Myreadingmanga.search_by_keyword('', False)