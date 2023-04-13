from bs4 import BeautifulSoup
from utils.Bases import Doujin, Req

class Nyahentai(Doujin, Req):
    def get_title(code):
        response = Nyahentai.send_request(f'https://nyahentai.red/g/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class', 'title'}).find('span').contents[0]
        return title

    def get_images(code):
        response = Nyahentai.send_request(f'https://nyahentai.red/g/{code}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('a', {'class': 'gallerythumb'})
        images = [div.find('img')['data-src'] for div in divs]
        new_images = []
        for image in images:
            name = image.rsplit('/', 1)[1]
            name = name.replace('t.', '.')
            new_images.append(f'{image.rsplit("/", 1)[0]}/{name}')
        return new_images

    def search(title, absolute):
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Nyahentai.send_request(f'https://nyahentai.red/search?q={title}&page={page}')
                soup = BeautifulSoup(response.text, 'html.parser')
                doujins = soup.find_all('div', {'class': 'gallery'})
                if len(doujins) == 0:
                    yield {}
                results = {}
                for doujin in doujins:
                    doj = doujin.find('a')
                    ti = doj.find('div', {'class': 'caption'}).contents[0]
                    if absolute and title.lower() not in ti.lower():
                        continue
                    results[ti] = {
                        'domain': 'nyahentai.red',
                        'code': doj['href'].split('/')[-2]
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
        return Nyahentai.search('', False)