from bs4 import BeautifulSoup
from utils.models import Doujin

class Nhentai_Net(Doujin):
    domain = 'nhentai.net'
    logo = 'https://static.nhentai.net/img/logo.090da3be7b51.svg'

    def get_info(code):
        from contextlib import suppress
        response, _ = Nhentai_Net.send_request(f'https://nhentai.net/g/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, pages, uploaded = 5 * ['']
        info_box = soup.find('div', {'id': 'info'})
        extras = {}
        with suppress(Exception):
            cover = soup.find('div', {'id': 'cover'}).find('img')['data-src']
        with suppress(Exception):
            title = info_box.find('h1').get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find('h2').get_text(strip=True)
        with suppress(Exception):
            uploaded = info_box.find('time')['datetime']
        with suppress(Exception):
            pages = info_box.find('section', {'id': 'tags'}).find(lambda tag: 'Pages:' in tag.text).get_text(strip=True).replace('Pages:', '')
        tag_box = soup.find('section', {'id': 'tags'}).find_all('div', {'class': 'tag-container field-name'})
        for box in tag_box:
            if 'Pages' in box.text or 'Uploaded' in box.text:
                continue
            with suppress(Exception):

                extras[box.contents[0].strip()] = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Pages': pages,
            'Alternative': alternative,
            'Extras': extras,
            'Dates': {
                'Uploaded': uploaded
            }
        }

    def get_title(code):
        response, _ = Nhentai_Net.send_request(f'https://nhentai.net/g/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class', 'title'}).find('span').get_text(strip=True)
        return title

    def get_images(code):
        response, _ = Nhentai_Net.send_request(f'https://nhentai.net/g/{code}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('a', {'class': 'gallerythumb'})
        images = [div.find('img')['data-src'] for div in divs]
        new_images = []
        for image in images:
            name = image.rsplit('/', 1)[1].replace('t.', '.')
            new_images.append(f'{image.replace("//t", "//i").rsplit("/", 1)[0]}/{name}')
        return new_images, False

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        page = 1
        template = f'search?q={keyword}&' if keyword else '?'
        while True:
            try:
                response, _ = Nhentai_Net.send_request(f'https://nhentai.net/{template}page={page}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'gallery'})
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                if absolute and keyword.lower() not in doujin.get_text(strip=True).lower():
                    continue
                results[doujin.get_text(strip=True)] = {
                    'domain': Nhentai_Net.domain,
                    'code': doujin.find('a')['href'].split('/')[-2],
                    'thumbnail': doujin.find('img')['data-src'],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Nhentai_Net.search_by_keyword('', False)