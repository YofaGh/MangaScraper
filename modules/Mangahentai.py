from bs4 import BeautifulSoup
from utils.models import Manga

class Mangahentai(Manga):
    domain = 'mangahentai.me'

    def get_chapters(manga):
        response = Mangahentai.send_request(f'https://mangahentai.me/manga-hentai/{manga}/ajax/chapters/', method='POST')
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters_urls = [li.find('a')['href'].split('/')[-2] for li in lis[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Mangahentai.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Mangahentai.send_request(f'https://mangahentai.me/manga-hentai/{manga}/{chapter["url"]}/')
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
                response = Mangahentai.send_request(f'https://mangahentai.me/page/{page}/?s={keyword}&post_type=wp-manga')
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
                        if 'Authors' in content.text:
                            authors = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Artists' in content.text:
                            artists = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Genres' in content.text:
                            genres = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Status' in content.text:
                            status = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[ti] = {
                    'domain': Mangahentai.domain,
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
        return Mangahentai.search_by_keyword('', False)