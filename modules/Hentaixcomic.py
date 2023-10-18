from bs4 import BeautifulSoup
from utils.models import Manga

class Hentaixcomic(Manga):
    domain = 'hentaixcomic.com'
    logo = 'https://hentaixcomic.com/wp-content/uploads/2020/07/cropped-Pg_00-1-192x192.jpg'

    def get_chapters(manga):
        response = Hentaixcomic.send_request(f'https://hentaixcomic.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        manga_id = soup.find('a', {'class': 'wp-manga-action-button'})['data-post']
        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = f'action=manga_get_chapters&manga={manga_id}'
        response = Hentaixcomic.send_request('https://hentaixcomic.com/wp-admin/admin-ajax.php', method='POST', headers=headers, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters_urls = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Hentaixcomic.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Hentaixcomic.send_request(f'https://hentaixcomic.com/manga/{manga}/{chapter["url"]}')
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
                response = Hentaixcomic.send_request(f'https://hentaixcomic.com/page/{page}/?s={keyword}&post_type=wp-manga')
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
                latest_chapter, genres, authors, status, release_date = '', '', '', '', ''
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
                            release_date = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[ti] = {
                    'domain': Hentaixcomic.domain,
                    'url': link,
                    'latest_chapter': latest_chapter,
                    'thumbnail': manga.find('img')['src'],
                    'genres': genres,
                    'authors': authors,
                    'status': status,
                    'release_date': release_date,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Hentaixcomic.search_by_keyword('', False)