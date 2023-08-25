from bs4 import BeautifulSoup
from utils.models import Manga

class Toonily_Com(Manga):
    domain = 'toonily.com'
    logo = 'https://toonily.com/wp-content/uploads/2020/01/cropped-toonfavicon-1-192x192.png'
    download_images_headers = {'Referer': 'https://toonily.com/'}
    search_headers = {'cookie': 'toonily-mature=1'}

    def get_chapters(manga):
        response = Toonily_Com.send_request(f'https://toonily.com/webtoon/{manga}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters_urls = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Toonily_Com.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Toonily_Com.send_request(f'https://toonily.com/webtoon/{manga}/{chapter["url"]}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        template = f'https://toonily.com/search/{keyword}/page/P_P_P_P/' if keyword else f'https://toonily.com/search/page/P_P_P_P/'
        page = 1
        while True:
            try:
                response = Toonily_Com.send_request(template.replace('P_P_P_P', str(page)), headers=Toonily_Com.search_headers)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'post-title font-title'})
            results = {}
            for manga in mangas:
                if absolute and keyword.lower() not in manga.get_text(strip=True).lower():
                    continue
                results[manga.get_text(strip=True)] = {
                    'domain': Toonily_Com.domain,
                    'url': manga.find('a')['href'].split('/')[-2],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Toonily_Com.search_by_keyword('', False)

class Toonily_Me(Manga):
    domain = 'toonily.me'
    logo = 'https://toonily.me/static/sites/toonily/icons/favicon.ico'
    download_images_headers = {'Referer': 'https://toonily.me/'}

    def get_chapters(manga):
        response = Toonily_Me.send_request(f'https://toonily.me/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('ul', {'class': 'chapter-list'}).find_all('li')
        chapters_urls = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Toonily_Me.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Toonily_Me.send_request(f'https://toonily.me/{manga}/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id': 'chapter-images'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        template = f'https://toonily.me/search?q={keyword}&page=P_P_P_P' if keyword else f'https://toonily.me/az-list?page=P_P_P_P'
        page = 1
        while True:
            response = Toonily_Me.send_request(template.replace('P_P_P_P', str(page)))
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'book-item'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'title'}).find('a')
                if absolute and keyword.lower() not in ti['title'].lower():
                    continue
                latest_chapter, genres, summary = '', '', ''
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'latest-chapter'})['title']
                with suppress(Exception): genres = manga.find('div', {'class': 'genres'}).get_text(strip=True, separator=', ')
                with suppress(Exception): summary = manga.find('div', {'class': 'summary'}).get_text(strip=True)
                results[ti['title']] = {
                    'domain': Toonily_Me.domain,
                    'url': ti['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'genres': genres,
                    'summary': summary,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Toonily_Me.search_by_keyword('', False)