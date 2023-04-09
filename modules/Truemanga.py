from bs4 import BeautifulSoup
from utils.Bases import Manga, Req

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
        return images, False

    def search(title, absolute):
        from utils.assets import waiter
        from requests. exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Truemanga.send_request(f'https://truemanga.com/search?q={title}&page={page}')
            except HTTPError:
                yield []
            except Timeout as error:
                raise error
            except RequestException:
                waiter()
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'book-item'})
            if len(mangas) == 0:
                yield []
            results = []
            for manga in mangas:
                ti = manga.find('div', {'class': 'title'}).find('a')['title']
                link = manga.find('div', {'class': 'title'}).find('a')['href'].split('/')[-1]
                if absolute and title.lower() not in ti.lower():
                    continue
                results.append(f'title: {ti}, url: {link}')
            yield results
            page += 1