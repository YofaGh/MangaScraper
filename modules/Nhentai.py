from bs4 import BeautifulSoup
from utils.Bases import Doujin

class Nhentai(Doujin):
    def get_title(code):
        response = Nhentai.send_request(f'https://nhentai.xxx/g/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class', 'title'}).find('span').contents[0]
        return title

    def get_images(code):
        response = Nhentai.send_request(f'https://nhentai.xxx/g/{code}/')
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
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Nhentai.send_request(f'https://nhentai.xxx/search?q={keyword}&page={page}')
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
                        'domain': 'nhentai.xxx',
                        'code': doj['href'].split('/')[-2],
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
        return Nhentai.search_by_keyword('', False)