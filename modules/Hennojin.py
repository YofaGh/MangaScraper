from bs4 import BeautifulSoup
from utils.models import Doujin

class Hennojin(Doujin):
    domain = 'hennojin.com'
    logo = 'https://hennojin.com/favicon.ico'
    is_coded = False

    def get_title(code, wait=True):
        response = Hennojin.send_request(f'https://hennojin.com/home/?manga={code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h3', {'class', 'manga-title'}).contents[0]
        return title

    def get_images(code, wait=True):
        code = code.replace('-', ' ')
        response = Hennojin.send_request(f'https://hennojin.com/home/manga-reader/?manga={code}&view=page', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'slideshow-container'}).find_all('img')
        images = [f'https://hennojin.com{image["src"]}' for image in images]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        data = {'action': 'post_grid_paginate_ajax_free', 'grid_id': '23', 'current_page': 1, 'formData': f'keyword={keyword}'}
        while True:
            response = Hennojin.send_request(f'https://hennojin.com/home/wp-admin/admin-ajax.php', method='POST', data=data, wait=wait).json()
            if not response.get('html'):
                yield {}
            soup = BeautifulSoup(response['html'], 'html.parser')
            doujins = soup.find_all('div', {'class': 'layer-content element_3'})
            results = {}
            for doujin in doujins:
                tilink = doujin.find('div', {'class': 'title_link'}).find('a')
                if absolute and keyword.lower() not in tilink.get_text(strip=True).lower():
                    continue
                results[tilink.get_text(strip=True)] = {
                    'domain': Hennojin.domain,
                    'code': tilink['href'],
                    'thumbnail': doujin.find('img')['src'],
                    'page': data['current_page']
                }
            yield results
            data['current_page'] += 1

    def get_db(wait=True):
        return Hennojin.search_by_keyword('', False, wait=wait)