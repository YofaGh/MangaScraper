from bs4 import BeautifulSoup
from utils.models import Manga

class Manytoon(Manga):
    domain = 'manytoon.com'

    def get_chapters(manga):
        response = Manytoon.send_request(f'https://manytoon.com/comic/{manga}/ajax/chapters/', method='POST')
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [li.find('a')['href'].split('/')[-2] for li in lis[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manytoon.send_request(f'https://manytoon.com/comic/{manga}/{chapter}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Manytoon.send_request(f'https://manytoon.com/page/{page}/?s={keyword}&post_type=wp-manga')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'post-title'}).find('a').get_text(strip=True)
                if absolute and keyword.lower() not in ti.lower():
                    continue
                link = manga.find('div', {'class': 'post-title'}).find('a')['href'].split('/')[-2]
                latest_chapter, genres, authors, status = '', '', '', ''
                contents = manga.find_all('div', {'class': 'post-content_item'})
                for content in contents:
                    with suppress(Exception):
                        if 'Authors' in content.text:
                            authors = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Genres' in content.text:
                            genres = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Status' in content.text:
                            status = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[ti] = {
                    'domain': Manytoon.domain,
                    'url': link,
                    'latest_chapter': latest_chapter,
                    'genres': genres,
                    'authors': authors,
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manytoon.search_by_keyword('', False)