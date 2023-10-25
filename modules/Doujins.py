from bs4 import BeautifulSoup
from utils.models import Doujin

class Doujins(Doujin):
    domain = 'doujins.com'
    logo = 'https://doujins.com/img/logo32x32.png'
    is_coded = False

    def get_title(code, wait=True):
        response = Doujins.send_request(f'https://doujins.com/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'folder-title'}).find_all('a')[-1].get_text(strip=True)
        return title

    def get_images(code, wait=True):
        response = Doujins.send_request(f'https://doujins.com/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        if 'Upgrade to premium now!' in soup.find('div', {'id', 'thumbnails'}).get_text():
            return [], False
        images = soup.find_all('img', {'class': 'doujin active'})
        images = [image['data-file'].replace('&amp;', '&') for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        page = 1
        while True:
            response = Doujins.send_request(f'https://doujins.com/searches?words={keyword}&page={page}', wait=wait)
            soup = BeautifulSoup(response.text, 'html.parser')
            soup = soup.select('#content > div > div:nth-child(5)')[0]
            doujins = soup.find_all('div', {'class': 'col-6 col-sm-4 col-md-3 col-lg-2 px-1'})
            if len(doujins) == 0:
                yield {}
            results = {}
            for doujin in doujins:
                tilink = doujin.find('a')
                if absolute and keyword.lower() not in tilink.get_text(strip=True).lower():
                    continue
                artist = ''
                with suppress(Exception): artist = doujin.find_all(lambda tag:tag.name == 'div' and 'Artist: ' in tag.text)[-1].get_text(strip=True)
                results[tilink.get_text(strip=True)] = {
                    'domain': Doujins.domain,
                    'code': tilink['href'][1:],
                    'thumbnail': doujin.find('img')['srcset'],
                    'artists': artist.replace('Artist: ', ''),
                    'page': page
                }
            yield results
            page += 1