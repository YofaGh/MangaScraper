from utils.Bases import Manga, Req
from bs4 import BeautifulSoup

class Skymanga(Manga, Req):
    def get_chapters(manga):
        response = Skymanga.send_request(f'https://skymanga.xyz/read/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Skymanga.send_request(f'https://skymanga.xyz/read/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class':'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images, False

    def search_by_title(title, sleep_time, absolute=False, limit_page=1000):
        import time
        results = {}
        page = 1
        while True:
            yield False, page
            if page > limit_page:
                break
            try:
                response = Skymanga.send_request(f'https://skymanga.xyz/page/{page}/?s={title}&post_type=wp-manga')
            except:
                break
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            for manga in mangas:
                ti = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['title']
                link = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['href'].split('/')[-2]
                if absolute and title.lower() not in ti.lower():
                    continue
                results[link] = ti
            page += 1
            time.sleep(sleep_time)
        yield True, results
        return