from bs4 import BeautifulSoup
from utils.models import Manga

class Manga18fx(Manga):
    domain = 'manga18fx.com'

    def get_chapters(manga):
        response = Manga18fx.send_request(f'https://manga18fx.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'a-h'})
        chapters_urls = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Manga18fx.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Manga18fx.send_request(f'https://manga18fx.com/manga/{manga}/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'read-content'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        from contextlib import suppress
        template = f'https://manga18fx.com/search?q={keyword}&page=P_P_P_P' if keyword else f'https://manga18fx.com/page/P_P_P_P'
        page = 1
        prev_page = []
        while True:
            try:
                response = Manga18fx.send_request(template.replace('P_P_P_P', str(page)))
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'bigor-manga'})
            results = {}
            if mangas == prev_page:
                yield {}
            for manga in mangas:
                ti = manga.find('h3', {'class': 'tt'}).find('a')
                if absolute and keyword.lower() not in ti['title'].lower():
                    continue
                with suppress(Exception): latest_chapter = manga.find('div', {'class': 'list-chapter'}).find('a')['href'].split('/')[-1]
                results[ti['title']] = {
                    'domain': Manga18fx.domain,
                    'url': ti['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            prev_page = mangas
            yield results
            page += 1

    def get_db():
        return Manga18fx.search_by_keyword('', False)