from utils.Bases import Manga, Req
from bs4 import BeautifulSoup

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

    def search_by_title(title, absolute=False, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield False, page
            if page > limit_page:
                break
            response = Manhuascan.send_request(f'https://manhuascan.us/manga-list?search={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'bsx'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                if absolute and title.lower() not in manga.find('a')['title'].lower():
                    continue
                results[manga.find('a')['href'].split('/')[-1]] = manga.find('a')['title']
            page += 1
        yield True, results
        return