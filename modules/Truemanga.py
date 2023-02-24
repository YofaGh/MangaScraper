from utils.Bases import Manga, Req
from bs4 import BeautifulSoup

class Truemanga(Manga, Req):
    def get_chapters(manga):
        response = Truemanga.send_request(f'https://truemanga.com/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('ul', {'class':'chapter-list'}).find_all('a')
        chapters = [link['href'].split('/')[-1] for link in links[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Truemanga.send_request(f'https://truemanga.com/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id':'chapter-images'}).find_all('img')
        images = [image['data-src'] for image in images]
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = Truemanga.send_request(f'https://truemanga.com/search?q={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'book-item'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                ti = manga.find('div', {'class': 'title'}).find('a')['title']
                link = manga.find('div', {'class': 'title'}).find('a')['href'].split('/')[-1]
                results[link] = ti
            page += 1
        yield results
        return