from bs4 import BeautifulSoup
from utils.models import Manga

class WMangairo(Manga):
    domain = 'w.mangairo.com'
    logo = 'https://w.mangairo.com/themes/home/images/favicon.png'
    download_images_headers = {'Referer': 'https://chap.mangairo.com/'}

    def get_info(manga, wait=True):
        from contextlib import suppress
        from datetime import datetime
        response = WMangairo.send_request(f'https://chap.mangairo.com/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser').find('div', {'class': 'story_content'})
        contents = soup.find('ul', {'class': 'story_info_right'}).find_all('li')
        cover, title, alternative, summary, status, authors, genres, view, last_updated = 9 * ['']
        with suppress(Exception): cover = soup.find('img')['src']
        with suppress(Exception): title = contents[0].find('h1').get_text(strip=True)
        with suppress(Exception): alternative = contents[1].find('h2').get_text(strip=True)
        with suppress(Exception): summary = soup.find('div', {'id': 'story_discription'}).find('p').contents[5].replace('\n', '').replace('\xa0', '')
        with suppress(Exception): status = contents[4].find('a').get_text(strip=True)
        with suppress(Exception): authors = [a.get_text(strip=True) for a in contents[2].find_all('a')]
        with suppress(Exception): genres = [a.get_text(strip=True) for a in contents[3].find_all('a')]
        with suppress(Exception): view = contents[6].contents[-1]
        with suppress(Exception): last_updated = datetime.strptime(contents[5].contents[-1].get_text(strip=True), '%b-%d-%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Status': status,
            'Extras': {
                'Authors': authors,
                'Genres': genres,
                'View': view
            },
            'Dates': {
                'Last updated': last_updated
            },
        }

    def get_chapters(manga, wait=True):
        response = WMangairo.send_request(f'https://chap.mangairo.com/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find('div', {'class': 'chapter_list'}).find_all('li')
        chapters_urls = [li.find('a')['href'].split('/')[-1] for li in lis[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': WMangairo.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = WMangairo.send_request(f'https://chap.mangairo.com/{manga}/{chapter["url"]}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'panel-read-story'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
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
                response = WMangairo.send_request(template.replace('P_P_P_P', str(page)), wait=wait)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'story-item'})
            if not mangas:
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
                    'thumbnail': manga.find('img')['src'],
                    'Authors': authors.replace('Author : ', '').replace('Author(s) : ', ''),
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            prev_page = mangas
            yield results
            page += 1

    def get_db(wait=True):
        return WMangairo.search_by_keyword('', False, wait=wait)