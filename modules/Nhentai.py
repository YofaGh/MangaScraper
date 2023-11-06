from bs4 import BeautifulSoup
from utils.models import Doujin

class Nhentai_Com(Doujin):
    domain = 'nhentai.com'
    logo = 'https://cdn.nhentai.com/nhentai/images/icon.png'
    headers = {'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)'}
    is_coded = False

    def get_info(code, wait=True):
        from datetime import datetime
        response = Nhentai_Com.send_request(f'https://nhentai.com/api/comics/{code}', headers=Nhentai_Com.headers, wait=wait).json()
        return {
            'Cover': response['image_url'],
            'Title': response['title'],
            'Pages': response['pages'],
            'Alternative': response['alternative_title'],
            'Extras': {
                'Parodies': [tag['name'] for tag in response['parodies']],
                'Characters': [tag['name'] for tag in response['characters']],
                'Tags': [tag['name'] for tag in response['tags']],
                'Artists': [tag['name'] for tag in response['artists']],
                'Authors': [tag['name'] for tag in response['authors']],
                'Groups': [tag['name'] for tag in response['groups']],
                'Languages': response['language']['name'] if response['language'] else '',
                'Category': response['category']['name'] if response['category'] else '',
                'Relationships': [tag['name'] for tag in response['relationships']]
            },
            'Dates': {
                'Uploaded At': datetime.strptime(response['uploaded_at'], '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S') if response['uploaded_at'] else ''
            }
        }

    def get_title(code, wait=True):
        response = Nhentai_Com.send_request(f'https://nhentai.com/api/comics/{code}', headers=Nhentai_Com.headers, wait=wait).json()
        return response['title']

    def get_images(code, wait=True):
        response = Nhentai_Com.send_request(f'https://nhentai.com/api/comics/{code}/images', headers=Nhentai_Com.headers, wait=wait).json()
        images = [image['source_url'] for image in response['images']]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        page = 1
        tail = '&sort=title' if not keyword else ''
        while True:
            response = Nhentai_Com.send_request(f'https://nhentai.com/api/comics?page={page}&q={keyword}{tail}', headers=Nhentai_Com.headers, wait=wait).json()
            doujins = response['data']
            if len(doujins) == 0:
                yield {}
            results = {}
            for doujin in doujins:
                if absolute and keyword.lower() not in doujin['title'].lower():
                    continue
                category, language, tags = '', '', ''
                with suppress(Exception): category = doujin['category']['name']
                with suppress(Exception): language = doujin['language']['name']
                with suppress(Exception): tags = ', '.join([tag['name'] for tag in doujin['tags']])
                results[doujin['title']] = {
                    'domain': Nhentai_Com.domain,
                    'code': doujin['slug'],
                    'thumbnail': doujin['image_url'],
                    'category': category,
                    'language': language,
                    'tags': tags,
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Nhentai_Com.search_by_keyword('', False, wait=wait)

class Nhentai_Xxx(Doujin):
    domain = 'nhentai.xxx'
    logo = 'https://nhentai.xxx/front/logo.svg'

    def get_info(code, wait=True):
        from contextlib import suppress
        response = Nhentai_Xxx.send_request(f'https://nhentai.xxx/g/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, pages, uploaded = 5 * ['']
        info_box = soup.find('div', {'id': 'info'})
        extras = {}
        with suppress(Exception): cover = soup.find('div', {'id': 'cover'}).find('img')['data-src']
        with suppress(Exception): title = info_box.find('h1').get_text(strip=True)
        with suppress(Exception): alternative = info_box.find('h2').get_text(strip=True)
        with suppress(Exception): uploaded = info_box.find('time')['datetime']
        with suppress(Exception): pages = info_box.find('section', {'id': 'tags'}).find(lambda tag: 'Pages:' in tag.text).get_text(strip=True).replace('Pages:', '')
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

    def get_title(code, wait=True):
        response = Nhentai_Xxx.send_request(f'https://nhentai.xxx/g/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class', 'title'}).find('span').get_text(strip=True)
        return title

    def get_images(code, wait=True):
        response = Nhentai_Xxx.send_request(f'https://nhentai.xxx/g/{code}/', wait=wait)
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
                response = Nhentai_Xxx.send_request(f'https://nhentai.xxx/search?q={keyword}&page={page}', wait=wait)
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
                    'domain': Nhentai_Xxx.domain,
                    'code': doujin.find('a')['href'].split('/')[-2],
                    'thumbnail': doujin.find('img')['src'],
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Nhentai_Xxx.search_by_keyword('', False, wait=wait)