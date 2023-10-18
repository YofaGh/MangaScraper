from bs4 import BeautifulSoup
from utils.models import Manga

class Manga68(Manga):
    domain = 'manga68.com'
    logo = 'https://manga68.com/wp-content/uploads/2017/10/cropped-manga68-2-192x192.png'

    def get_chapters(manga):
        response = Manga68.send_request(f'https://manga68.com/manga/{manga}/ajax/chapters/', method='POST')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters_urls = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Manga68.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Manga68.send_request(f'https://manga68.com/manga/{manga}/{chapter["url"]}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class':'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Manga68.send_request(f'https://manga68.com/page/{page}/?s={keyword}&post_type=wp-manga')
            except HTTPError:
                yield {}
            if response.url == f'https://manga68.com?s={keyword}&post_type=wp-manga':
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            results = {}
            for manga in mangas:
                tilink = manga.find('div', {'class', 'post-title'})
                if absolute and keyword.lower() not in tilink.get_text(strip=True).lower():
                    continue
                latest_chapter, authors, artists, genres, status, release_date = '', '', '', '', '', ''
                contents = manga.find_all('div', {'class': 'post-content_item'})
                for content in contents:
                    with suppress(Exception):
                        if 'Authors' in content.text:
                            authors = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Artists' in content.text:
                            artists = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Genres' in content.text:
                            genres = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Status' in content.text:
                            status = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Release' in content.text:
                            release_date = content.find('a').get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[tilink.get_text(strip=True)] = {
                    'domain': Manga68.domain,
                    'url': tilink.find('a')['href'].split('/')[-2],
                    'latest_chapter': latest_chapter,
                    'thumbnail': manga.find('img')['data-src'],
                    'genres': genres,
                    'authors': authors,
                    'artists': artists,
                    'status': status,
                    'release_date': release_date,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manga68.search_by_keyword('', False)