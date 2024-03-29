from utils.models import Doujin

class _9hentai(Doujin):
    domain = '9hentai.to'
    logo = 'https://9hentai.to/images/logo.png'

    def get_info(code, wait=True):
        from bs4 import BeautifulSoup
        from contextlib import suppress
        response = _9hentai.send_request(f'https://9hentai.to/g/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, pages, uploaded = 5 * ['']
        info_box = soup.find('div', {'id': 'info'})
        extras = {}
        with suppress(Exception): cover = soup.find('div', {'id': 'cover'}).find('v-lazy-image')['src']
        with suppress(Exception): title = info_box.find('h1').get_text(strip=True)
        with suppress(Exception): alternative = info_box.find('h2').get_text(strip=True)
        with suppress(Exception): extras['Uploaded'] = info_box.find('time').get_text(strip=True)
        with suppress(Exception): pages = info_box.find(lambda tag: 'pages' in tag.text).get_text(strip=True).replace(' pages', '')
        tag_box = soup.find('section', {'id': 'tags'}).find_all('div', {'class': 'tag-container field-name'})
        for box in tag_box:
            with suppress(Exception): 
                extras[box.contents[0].strip()[:-1]] = [link.get_text(strip=True) for link in box.find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Pages': pages,
            'Alternative': alternative,
            'Extras': extras
        }

    def get_title(code, wait=True):
        response = _9hentai.send_request('https://9hentai.to/api/getBookByID', method='POST', json={'id':26487}, wait=wait).json()
        return response['results']['title']

    def get_images(code, wait=True):
        response = _9hentai.send_request('https://9hentai.to/api/getBookByID', method='POST', json={'id':26487}, wait=wait).json()
        images = [f'{response["results"]["image_server"]}{code}/{i+1}.jpg' for i in range(response['results']['total_page'])]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        json = {
            'search': {
                'text': keyword,
                'page': 0,
                'sort': 3 if keyword else 4,
                'pages': {
                    'range': [0,2000]
                },
                'tag': {
                    'text': '',
                    'type': 1,
                    'tags': [],
                    'items': {
                        'included': [],
                        'excluded': []
                    }
                }
            }
        }
        while True:
            response = _9hentai.send_request('https://9hentai.to/api/getBook', method='POST', json=json, wait=wait).json()
            doujins = response['results']
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                if absolute and keyword.lower() not in doujin['title'].lower():
                    continue
                results[doujin['title']] = {
                    'domain': _9hentai.domain,
                    'code': doujin['id'],
                    'thumbnail': f'{doujin["image_server"]}{doujin["id"]}/cover-small.jpg',
                    'tags': ', '.join([tag['name'] for tag in doujin['tags']]),
                    'page': json['search']['page'] + 1
                }
            yield results
            json['search']['page'] += 1

    def get_db(wait=True):
        return _9hentai.search_by_keyword('', False, wait=wait)