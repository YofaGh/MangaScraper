from bs4 import BeautifulSoup
from utils.models import Manga

class Manga18h(Manga):
    domain = 'manga18h.com'

    def get_chapters(manga):
        response = Manga18h.send_request(f'https://manga18h.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manga18h.send_request(f'https://manga18h.com/manga/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Manga18h.send_request(f'https://manga18h.com/page/{page}/?s={keyword}&post_type=wp-manga')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['title']
                if absolute and keyword.lower() not in ti.lower():
                    continue
                link = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['href'].split('/')[-2]
                latest_chapter, genres, authors, artists, status = '', '', '', '', ''
                contents = manga.find_all('div', {'class': 'post-content_item'})
                for content in contents:
                    with suppress(Exception):
                        head = content.find('h5').contents[0].replace('\n', '').replace(' ', '').replace('\t', '')
                        if head == 'Authors':
                            authors = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Artists':
                            artists = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Genres':
                            genres = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Status':
                            status = content.find('div', {'class': 'summary-content'}).contents[0].replace('\n', '').replace(' ', '').replace('\t', '')
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[ti] = {
                    'domain': Manga18h.domain,
                    'url': link,
                    'latest_chapter': latest_chapter,
                    'genres': genres,
                    'authors': authors,
                    'artists': artists,
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manga18h.search_by_keyword('', False)