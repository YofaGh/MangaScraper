from bs4 import BeautifulSoup
from utils.models import Doujin

class Imhentai(Doujin):
    domain = 'imhentai.xxx'

    def get_title(code):
        response = Imhentai.send_request(f'https://imhentai.xxx/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'col-md-7 col-sm-7 col-lg-8 right_details'}).find('h1').contents[0]
        return title

    def get_images(code):
        response = Imhentai.send_request(f'https://imhentai.xxx/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        sample = soup.find('div', {'id': 'append_thumbs'}).find('img')['data-src']
        sample_path = sample.rsplit('/', 1)[0]
        sample_format = sample.rsplit('.', 1)[1]
        pages = int(soup.find('li', {'class': 'pages'}).contents[0].split(' ')[-1])
        images = [f'{sample_path}/{i}.{sample_format}' for i in range(1, pages+1)]
        return images

    def search_by_keyword(keyword, absolute):
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Imhentai.send_request(f'https://imhentai.xxx/search/?key={keyword}&page={page}')
                soup = BeautifulSoup(response.text, 'html.parser')
                doujins = soup.find_all('div', {'class': 'thumb'})
                if len(doujins) == 0:
                    yield {}
                results = {}
                for doujin in doujins:
                    caption = doujin.find('div', {'class': 'caption'})
                    ti = caption.find('a').contents[0]
                    if absolute and keyword.lower() not in ti.lower():
                        continue
                    results[ti] = {
                        'domain': Imhentai.domain,
                        'code': caption.find('a')['href'].split('/')[-2],
                        'category': doujin.find('a', {'class':'thumb_cat'}).contents[0],
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
        return Imhentai.search_by_keyword('', False)