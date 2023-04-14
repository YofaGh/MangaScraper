from bs4 import BeautifulSoup
from utils.Bases import Manga, Req

class Manhuascan(Manga, Req):
    def get_chapters(manga):
        response = Manhuascan.send_request(f'https://manhuascan.us/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'eph-num'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manhuascan.send_request(f'https://manhuascan.us/manga/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id': 'readerarea'}).find_all('img')
        images = [image['src'] for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from utils.assets import waiter
        from contextlib import suppress
        from requests.exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Manhuascan.send_request(f'https://manhuascan.us/manga-list?search={keyword}&page={page}')
                soup = BeautifulSoup(response.text, 'html.parser')
                mangas = soup.find_all('div', {'class': 'bsx'})
                if len(mangas) == 0:
                    yield {}
                results = {}
                for manga in mangas:
                    ti = manga.find('a')['title']
                    if absolute and keyword.lower() not in ti.lower():
                        continue
                    latest_chapter = ''
                    with suppress(Exception): latest_chapter = manga.find('div', {'class': 'adds'}).find('a')['href'].split('/')[-1]
                    results[ti] = {
                        'domain': 'manhuascan.us',
                        'url': manga.find('a')['href'].split('/')[-1],
                        'latest_chapter': latest_chapter,
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
        return Manhuascan.search_by_keyword('', False)