from bs4 import BeautifulSoup
from utils.models import Manga

class Mangapill(Manga):
    domain = 'mangapill.com'
    logo = 'https://mangapill.com/static/favicon/favicon.ico'
    download_images_headers = {'Referer': 'https://mangapill.com/'}

    def get_info(manga):
        from contextlib import suppress
        response = Mangapill.send_request(f'https://mangapill.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, summary, status, genres, typee, year = 7 * ['']
        info_box = soup.find('div', {'class': 'grid grid-cols-1 md:grid-cols-3 gap-3 mb-3'}).find_all('div', recursive=False)
        with suppress(Exception): cover = soup.find('img')['data-src']
        with suppress(Exception): title = soup.find('h1').get_text(strip=True)
        with suppress(Exception): summary = soup.find('p').get_text(strip=True)
        with suppress(Exception): typee = info_box[0].find('div').get_text(strip=True)
        with suppress(Exception): status = info_box[1].find('div').get_text(strip=True)
        with suppress(Exception): year = info_box[2].find('div').get_text(strip=True)
        with suppress(Exception): genres = [a.get_text(strip=True) for a in soup.find('div', {'class': 'flex flex-col'}).find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Summary': summary,
            'Status': status,
            'Extras': {
                'Year': year,
                'Type': typee,
                'Genres': genres
            }
        }

    def get_chapters(manga):
        response = Mangapill.send_request(f'https://mangapill.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        chapters = [aa['href'].replace('/chapters/', '') for aa in soup.find('div', {'id': 'chapters'}).find_all('a')]
        chapters = [{
            'url': url,
            'name': Mangapill.rename_chapter(url.split('/')[-1])
        } for url in chapters[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Mangapill.send_request(f'https://mangapill.com/chapters/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('chapter-page')
        images = [div.find('img')['data-src'] for div in divs]
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        while True:
            response = Mangapill.send_request(f'https://mangapill.com/search?q={keyword}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find('div', {'class': 'my-3 grid justify-end gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-5'}).find_all('div', recursive=False)
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('a', {'class': 'mb-2'})
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                typee, status, year = '', '', ''
                info = manga.find('div', {'class': 'flex flex-wrap gap-1 mt-1'}).find_all('div')
                with suppress(Exception): typee = info[0].get_text(strip=True)
                with suppress(Exception): year = info[1].get_text(strip=True)
                with suppress(Exception): status = info[2].get_text(strip=True)
                results[ti.get_text(strip=True)] = {
                    'domain': Mangapill.domain,
                    'url': ti['href'].replace('/manga/', ''),
                    'thumbnail': manga.find('img')['data-src'],
                    'type': typee,
                    'status': status,
                    'year': year,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        from contextlib import suppress
        statuses = ['publishing', 'finished', 'on hiatus', 'discontinued', 'not yet published']
        for status in statuses:
            page = 1
            while True:
                response = Mangapill.send_request(f'https://mangapill.com/search?status={status}&page={page}')
                soup = BeautifulSoup(response.text, 'html.parser')
                mangas = soup.find('div', {'class': 'my-3 grid justify-end gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-5'}).find_all('div', recursive=False)
                if not mangas:
                    break
                results = {}
                for manga in mangas:
                    ti = manga.find('a', {'class': 'mb-2'})
                    typee, year = '', ''
                    info = manga.find('div', {'class': 'flex flex-wrap gap-1 mt-1'}).find_all('div')
                    with suppress(Exception): typee = info[0].get_text(strip=True)
                    with suppress(Exception): year = info[1].get_text(strip=True)
                    results[ti.get_text(strip=True)] = {
                        'domain': Mangapill.domain,
                        'url': ti['href'].replace('/manga/', ''),
                        'thumbnail': manga.find('img')['data-src'],
                        'type': typee,
                        'status': status,
                        'year': year,
                        'page': page
                    }
                yield results
                page += 1
        yield {}