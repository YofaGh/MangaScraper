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

    def search_by_keyword(keyword, absolute):
        from utils.assets import waiter
        from contextlib import suppress
        from requests.exceptions import RequestException, HTTPError, Timeout
        template = f'https://truemanga.com/search?q={keyword}&page=P_P_P_P' if keyword else 'https://truemanga.com/az-list?page=P_P_P_P'
        page = 1
        while True:
            try:
                response = Truemanga.send_request(template.replace('P_P_P_P', str(page)))
                soup = BeautifulSoup(response.text, 'html.parser')
                mangas = soup.find_all('div', {'class': 'book-item'})
                if len(mangas) == 0:
                    yield {}
                results = {}
                for manga in mangas:
                    ti = manga.find('div', {'class': 'title'}).find('a')['title']
                    if absolute and keyword.lower() not in ti.lower():
                        continue
                    latest_chapter, genres, summary = '', '', ''
                    with suppress(Exception): latest_chapter = manga.find('span', {'class': 'latest-chapter'})['title']
                    with suppress(Exception):
                        genres = manga.find('div', {'class': 'genres'}).find_all('span')
                        genres = ', '.join([genre.contents[0] for genre in genres])
                    with suppress(Exception): summary = manga.find('div', {'class': 'summary'}).find('p').contents[0]
                    results[ti] = {
                        'domain': 'truemanga.com',
                        'url': manga.find('div', {'class': 'title'}).find('a')['href'].split('/')[-1],
                        'latest_chapter': latest_chapter,
                        'genres': genres,
                        'summary': summary,
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
        return Truemanga.search_by_keyword('', False)