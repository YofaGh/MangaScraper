from utils.Bases import Doujin, Req
from bs4 import BeautifulSoup

class Nhentai(Doujin, Req):
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

    def search(title, sleep_time, absolute=False, limit_page=1000):
        import time
        results = []
        page = 1
        while page <= limit_page:
            yield False, page
            response = Nhentai.send_request(f'https://nhentai.xxx/search?q={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'gallery'})
            if len(doujins) == 0:
                break
            for doujin in doujins:
                doj = doujin.find('a')
                ti = doj.find('div', {'class': 'caption'}).contents[0]
                if absolute and title.lower() not in ti.lower():
                    continue
                results.append(f'title: {ti}, code: {doj["href"].split("/")[-2]}')
            page += 1
            time.sleep(sleep_time)
        yield True, results
        return