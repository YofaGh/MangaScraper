from bs4 import BeautifulSoup
from utils.models import Doujin

class Imhentai(Doujin):
    domain = 'imhentai.xxx'
    logo = 'https://imhentai.xxx/images/logo.png'
    image_formats = {
        'j': 'jpg',
        'p': 'png',
        'b': 'bmp',
        'g': 'gif'
    }

    def get_title(code, wait=True):
        response = Imhentai.send_request(f'https://imhentai.xxx/gallery/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'col-md-7 col-sm-7 col-lg-8 right_details'}).find('h1').get_text(strip=True)
        return title

    def get_images(code, wait=True):
        import json
        response = Imhentai.send_request(f'https://imhentai.xxx/gallery/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        path = soup.find('div', {'id': 'append_thumbs'}).find('img')['data-src'].rsplit('/', 1)[0]
        script = soup.find(lambda tag:tag.name == 'script' and 'var g_th' in tag.text).text
        images = json.loads(script.replace("var g_th = $.parseJSON('", '')[:-4])
        images = [f'{path}/{image}.{Imhentai.image_formats[images[image][0]]}' for image in images]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Imhentai.send_request(f'https://imhentai.xxx/search/?key={keyword}&page={page}', wait=wait)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'thumb'})
            if len(doujins) == 0:
                yield {}
            results = {}
            for doujin in doujins:
                caption = doujin.find('div', {'class': 'caption'})
                ti = caption.find('a').get_text()
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    'domain': Imhentai.domain,
                    'code': caption.find('a')['href'].split('/')[-2],
                    'category': doujin.find('a', {'class':'thumb_cat'}).get_text(),
                    'thumbnail': doujin.find('div', {'class': 'inner_thumb'}).find('img')['data-src'],
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Imhentai.search_by_keyword('', False, wait=wait)