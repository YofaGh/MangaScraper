from bs4 import BeautifulSoup
from utils.models import Manga

class Truemanga(Manga):
    domain = 'truemanga.com'
    logo = 'https://truemanga.com/static/sites/truemanga/icons/favicon.ico'
    download_images_headers = {'Referer': 'https://truemanga.com/'}

    def get_info(manga):
        from contextlib import suppress
        response, _ = Truemanga.send_request(f'https://truemanga.com/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, status = 5 * ['']
        extras = {}
        info_box = soup.find('div', {'class': 'book-info'})
        with suppress(Exception):
            cover = info_box.find('div', {'class': 'img-cover'}).find('img')['data-src']
        with suppress(Exception):
            title = info_box.find('div', {'class': 'name box'}).find('h1').get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find('div', {'class': 'name box'}).find('h2').get_text(strip=True)
        with suppress(Exception):
            summary = soup.find('div', {'class': 'section-body summary'}).find('p').get_text(strip=True)
        for p in info_box.find('div', {'class': 'meta box mt-1 p-10'}).find_all('p'):
            if 'Status' in p.get_text():
                status = p.find('span').get_text(strip=True)
            else:
                if len(p.find_all('a')) <= 1:
                    extras[p.find('strong').get_text(strip=True).replace(':', '').strip()] = p.find('span').get_text(strip=True)
                else:
                    extras[p.find('strong').get_text(strip=True).replace(':', '').strip()] = [a.text.replace(' ', '').replace('\n,', '').strip() for a in p.find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Status': status,
            'Extras': extras
        }

    def get_chapters(manga):
        response, session = Truemanga.send_request(f'https://truemanga.com/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag:tag.name == 'script' and 'bookId' in tag.text).text
        book_id = script.split('bookId = ')[1].split(';', 1)[0]
        response, session = Truemanga.send_request(f'https://truemanga.com/api/manga/{book_id}/chapters', session=session)
        soup = BeautifulSoup(response.text, 'html.parser')
        chapters = [{
            'url': chapter['value'].split('/')[-1],
            'name': chapter.get_text(strip=True)
        } for chapter in soup.find_all('option')[::-1]]
        return chapters

    def get_images(manga, chapter):
        response, _ = Truemanga.send_request(f'https://truemanga.com/{manga}/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag:tag.name == 'script' and 'chapImages' in tag.text).text
        images = script.replace("var chapImages = '", '').strip()[:-1].split(',')
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        template = f'https://truemanga.com/search?q={keyword}&page=P_P_P_P' if keyword else 'https://truemanga.com/az-list?page=P_P_P_P'
        page = 1
        session = None
        while True:
            try:
                response, session = Truemanga.send_request(template.replace('P_P_P_P', str(page)), session=session)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'book-item'})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'title'}).find('a')['title']
                if absolute and keyword.lower() not in ti.lower():
                    continue
                latest_chapter, genres, summary = '', '', ''
                with suppress(Exception):
                    latest_chapter = manga.find('span', {'class': 'latest-chapter'})['title']
                with suppress(Exception):
                    genres = manga.find('div', {'class': 'genres'}).get_text(strip=True, separator=', ')
                with suppress(Exception):
                    summary = manga.find('div', {'class': 'summary'}).get_text(strip=True)
                results[ti] = {
                    'domain': Truemanga.domain,
                    'url': manga.find('div', {'class': 'title'}).find('a')['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'thumbnail': manga.find('img')['data-src'],
                    'genres': genres,
                    'summary': summary,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Truemanga.search_by_keyword('', False)