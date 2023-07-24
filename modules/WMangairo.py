from bs4 import BeautifulSoup
from utils.models import Manga

class WMangairo(Manga):
    domain = 'w.mangairo.com'
    download_images_headers = {'Referer': 'https://chap.mangairo.com/'}

    def get_chapters(manga):
        response = WMangairo.send_request(f'https://chap.mangairo.com/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find('div', {'class': 'chapter_list'}).find_all('li')
        chapters = [li.find('a')['href'].split('/')[-1] for li in lis[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = WMangairo.send_request(f'https://chap.mangairo.com/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'panel-read-story'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        template = f'https://w.mangairo.com/list/search/{keyword}?page=P_P_P_P'
        if not keyword:
            template = 'https://w.mangairo.com/manga-list/type-latest/ctg-all/state-all/page-P_P_P_P'
        title_tag = 'h2' if keyword else 'h3'
        prev_page = []
        while True:
            try:
                response = WMangairo.send_request(template.replace('P_P_P_P', str(page)))
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'story-item'})
            if len(mangas) == 0:
                yield {}
            results = {}
            if mangas == prev_page:
                yield {}
            for manga in mangas:
                ti = manga.find(title_tag, {'class': 'story-name'})
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                authors, latest_chapter = '', ''
                with suppress(Exception): latest_chapter = manga.find('a', {'class': 'chapter-name'})['href'].split('/')[-1]
                with suppress(Exception): authors = manga.find(lambda tag:tag.name == 'span' and 'Author' in tag.text).get_text(strip=True)
                results[ti.get_text(strip=True)] = {
                    'domain': WMangairo.domain,
                    'url': ti.find('a')['href'].split('/')[-1],
                    'Authors': authors.replace('Author : ', '').replace('Author(s) : ', ''),
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            prev_page = mangas
            yield results
            page += 1

    def get_db():
        return WMangairo.search_by_keyword('', False)