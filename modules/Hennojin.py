from bs4 import BeautifulSoup
from utils.models import Doujin

class Hennojin(Doujin):
    domain = 'hennojin.com'
    logo = 'https://hennojin.com/favicon.ico'
    is_coded = False

    def get_info(code, wait=True):
        from contextlib import suppress
        response = Hennojin.send_request(f'https://hennojin.com/home/?manga={code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative = 3 * ['']
        info_box = soup.find('div', {'class': 'col-lg-9'})
        extras = {}
        with suppress(Exception): cover = soup.find('div', {'class': 'manga-thumbnail'}).find('img')['src']
        with suppress(Exception): title = soup.find('h3', {'class', 'manga-title'}).contents[0]
        with suppress(Exception): alternative = soup.find('h3', {'class', 'manga-title'}).contents[-1].strip()
        for box in info_box.find('p', {'data-pm-slice': '1 1 []'}).get_text().split('\n'):
            extras[box.split(': ')[0]] = box.split(': ')[1]
        attr, lis = None, []
        for child in info_box.find('p', {'class': 'tags-list'}).children:
            if child.name == 'span':
                if attr:
                    extras[attr] = lis
                attr = child.get_text(strip=True)
                lis = []
            elif child.get_text(strip=True):
                lis.append(child.get_text(strip=True))
        extras[attr] = lis
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Extras': extras
        }

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