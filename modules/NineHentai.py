from utils.models import Doujin

class NineHentai(Doujin):
    domain = '9hentai.to'
    logo = 'https://9hentai.to/images/logo.png'

    def get_title(code, wait=True):
        response = NineHentai.send_request('https://9hentai.to/api/getBookByID', method='POST', json={'id':26487}, wait=wait).json()
        return response['results']['title']

    def get_images(code, wait=True):
        response = NineHentai.send_request('https://9hentai.to/api/getBookByID', method='POST', json={'id':26487}, wait=wait).json()
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
            response = NineHentai.send_request('https://9hentai.to/api/getBook', method='POST', json=json, wait=wait).json()
            doujins = response['results']
            if len(doujins) == 0:
                yield {}
            results = {}
            for doujin in doujins:
                if absolute and keyword.lower() not in doujin['title'].lower():
                    continue
                results[doujin['title']] = {
                    'domain': NineHentai.domain,
                    'code': doujin['id'],
                    'thumbnail': f'{doujin["image_server"]}{doujin["id"]}/cover-small.jpg',
                    'tags': ', '.join([tag['name'] for tag in doujin['tags']]),
                    'page': json['search']['page'] + 1
                }
            yield results
            json['search']['page'] += 1

    def get_db(wait=True):
        return NineHentai.search_by_keyword('', False, wait=wait)