from bs4 import BeautifulSoup
from utils.models import Doujin

class Hentaifox(Doujin):
    domain = 'hentaifox.com'
    logo = 'https://hentaifox.com/images/logo.png'
    image_formats = {
        'j': 'jpg',
        'p': 'png',
        'b': 'bmp',
        'g': 'gif'
    }

    def get_title(code):
        response = Hentaifox.send_request(f'https://hentaifox.com/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'info'}).find('h1').get_text(strip=True)
        return title

    def get_images(code):
        import json
        response = Hentaifox.send_request(f'https://hentaifox.com/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        path = soup.find('div', {'class': 'gallery_thumb'}).find('img')['data-src'].rsplit('/', 1)[0]
        script = soup.find(lambda tag:tag.name == 'script' and 'var g_th' in tag.text).text
        images = json.loads(script.replace("var g_th = $.parseJSON('", '')[:-4])
        images = [f'{path}/{image}.{Hentaifox.image_formats[images[image][0]]}' for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Hentaifox.send_request(f'https://hentaifox.com/search/?q={keyword}&page={page}')
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
                    'domain': Hentaifox.domain,
                    'code': caption.find('a')['href'].split('/')[-2],
                    'category': doujin.find('a', {'class':'t_cat'}).get_text(),
                    'thumbnail': doujin.find('img')['src'],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        from requests.exceptions import HTTPError
        response = Hentaifox.send_request('https://hentaifox.com/categories/')
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.find('div', {'class': 'list_tags'}).find_all('a')
        categories = [a['href'] for a in categories]
        for category in categories:
            page = 1
            while True:
                try:
                    response = Hentaifox.send_request(f'https://hentaifox.com{category}pag/{page}/')
                except HTTPError:
                    break
                soup = BeautifulSoup(response.text, 'html.parser')
                doujins = soup.find_all('div', {'class': 'thumb'})
                if len(doujins) == 0:
                    break
                results = {}
                for doujin in doujins:
                    caption = doujin.find('div', {'class': 'caption'})
                    ti = caption.find('a').get_text()
                    results[ti] = {
                        'domain': Hentaifox.domain,
                        'code': caption.find('a')['href'].split('/')[-2],
                        'category': doujin.find('a', {'class':'t_cat'}).get_text()
                    }
                yield results
                page += 1
        yield {}