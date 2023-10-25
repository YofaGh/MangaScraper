from bs4 import BeautifulSoup
from utils.models import Doujin

class Nyahentai(Doujin):
    domain = 'nyahentai.red'
    logo = 'https://nyahentai.red/front/logo.svg'

    def get_info(code, wait=True):
        from contextlib import suppress
        response = Nyahentai.send_request(f'https://nyahentai.red/g/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, parodies, characters, tags, artists, groups, languages, categories, pages, uploaded = 12 * ['']
        with suppress(Exception): cover = soup.find('div', {'id': 'cover'}).find('img')['src']
        with suppress(Exception): title = soup.find('h1', {'class', 'title'}).find('span').get_text(strip=True)
        with suppress(Exception): alternative = soup.find('h2', {'class', 'title'}).find('span').get_text(strip=True)
        tag_box = soup.find('section', {'id': 'tags'}).find_all('div', {'class': 'tag-container field-name'})
        for box in tag_box:
            with suppress(Exception): 
                if 'Parodies' in box.text:
                    parodies = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
                elif 'Characters' in box.text:
                    characters = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
                elif 'Tags' in box.text:
                    tags = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
                elif 'Artists' in box.text:
                    artists = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
                elif 'Groups' in box.text:
                    groups = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
                elif 'Languages' in box.text:
                    languages = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
                elif 'Categories' in box.text:
                    categories = [link.find('span', {'class': 'name'}).get_text(strip=True) for link in box.find_all('a')]
                elif 'Pages:' in box.text:
                    pages = box.find('a').get_text(strip=True)
                elif 'Uploaded:' in box.text:
                    uploaded = box.find('time')['datetime']
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Parodies': parodies,
            'Characters': characters,
            'Tags': tags,
            'Artists': artists,
            'Groups': groups,
            'Languages': languages,
            'Categories': categories,
            'Pages': pages,
            'Uploaded': uploaded
        }

    def get_title(code, wait=True):
        response = Nyahentai.send_request(f'https://nyahentai.red/g/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class', 'title'}).find('span').get_text(strip=True)
        return title

    def get_images(code, wait=True):
        response = Nyahentai.send_request(f'https://nyahentai.red/g/{code}/', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('a', {'class': 'gallerythumb'})
        images = [div.find('img')['data-src'] for div in divs]
        new_images = []
        for image in images:
            name = image.rsplit('/', 1)[1]
            name = name.replace('t.', '.')
            new_images.append(f'{image.rsplit("/", 1)[0]}/{name}')
        return new_images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Nyahentai.send_request(f'https://nyahentai.red/search?q={keyword}&page={page}', wait=wait)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'gallery'})
            if len(doujins) == 0:
                yield {}
            results = {}
            for doujin in doujins:
                if absolute and keyword.lower() not in doujin.get_text(strip=True).lower():
                    continue
                results[doujin.get_text(strip=True)] = {
                    'domain': Nyahentai.domain,
                    'code': doujin.find('a')['href'].split('/')[-2],
                    'thumbnail': doujin.find('img')['src'],
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Nyahentai.search_by_keyword('', False, wait=wait)