from bs4 import BeautifulSoup
from utils.models import Doujin

class Ehentai(Doujin):
    domain = 'ehentai.to'
    logo = 'https://ehentai.to/favicon.ico'
    download_images_headers = {'Referer': 'https://ehentai.to/'}

    def get_info(code, wait=True):
        from contextlib import suppress
        response = Ehentai.send_request(f'https://ehentai.to/g/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, pages, uploaded = 5 * ['']
        info_box = soup.find('div', {'id': 'info'})
        extras = {}
        with suppress(Exception): cover = soup.find('div', {'id': 'cover'}).find('img')['data-src']
        with suppress(Exception): title = info_box.find('h1').get_text(strip=True)
        with suppress(Exception): alternative = info_box.find('h2').get_text(strip=True)
        with suppress(Exception): uploaded = info_box.find('time')['datetime']
        with suppress(Exception): pages = info_box.find(lambda tag: 'pages' in tag.text).get_text(strip=True).replace(' pages', '')
        tag_box = soup.find('section', {'id': 'tags'}).find_all('div', {'class': 'tag-container field-name'})
        for box in tag_box:
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

    def get_title(code, wait=True):
        response = Ehentai.send_request(f'https://ehentai.to/g/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'container'}).find('h1').get_text(strip=True)
        return title

    def get_images(code, wait=True):
        response = Ehentai.send_request(f'https://ehentai.to/g/{code}/', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('a', {'class': 'gallerythumb'})
        images = [div.find('img')['data-src'] for div in divs]
        new_images = []
        for image in images:
            name = image.rsplit('/', 1)[1].replace('t.', '.')
            new_images.append(f'{image.rsplit("/", 1)[0]}/{name}')
        return new_images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Ehentai.send_request(f'https://ehentai.to/search?q={keyword}&page={page}', wait=wait)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'gallery'})
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                doj = doujin.find('a')
                ti = doj.find('div', {'class': 'caption'}).get_text(strip=True)
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    'domain': Ehentai.domain,
                    'code': doj['href'].split('/')[-2],
                    'thumbnail': doj.find('img')['data-src'],
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Ehentai.search_by_keyword('', False, wait=wait)