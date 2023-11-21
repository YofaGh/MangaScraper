from bs4 import BeautifulSoup
from utils.models import Manga

class Omegascans(Manga):
    domain = 'omegascans.org'
    logo = 'https://omegascans.org/icon.png'

    def get_info(manga, wait=True):
        from contextlib import suppress
        from urllib.parse import unquote
        response = Omegascans.send_request(f'https://omegascans.org/series/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, release_year, authors = 6 * ['']
        with suppress(Exception): 
            cover = unquote(soup.find('div', {'class': 'lg:absolute flex flex-col items-center justify-center gap-y-2 w-full'}).find('img')['src'].replace('/_next/image?url=', ''))
        with suppress(Exception): title = soup.find('div', {'class': 'col-span-12 lg:col-span-9'}).find('h1').get_text(strip=True)
        with suppress(Exception): alternative = soup.find('div', {'class': 'col-span-12 lg:col-span-9'}).find('p').get_text(strip=True)
        with suppress(Exception): summary = soup.find('div', {'class': 'bg-gray-800 text-gray-50 rounded-xl p-5'}).get_text(strip=True)
        with suppress(Exception): 
            authors = soup.find('div', {'class': 'flex flex-col gap-y-2'}).find(lambda t: t.name == 'p' and 'Author' in t.text).find('strong').get_text(strip=True)
        with suppress(Exception): 
            release_year = soup.find('div', {'class': 'flex flex-col gap-y-2'}).find(lambda t: t.name == 'p' and 'Release' in t.text).find('strong').get_text(strip=True)
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Extras': {
                'Authors': authors,
                'Release Year': release_year
            }
        }

    def get_chapters(manga, wait=True):
        response = Omegascans.send_request(f'https://omegascans.org/series/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('ul', {'class': 'grid grid-cols-1 lg:grid-cols-3 gap-x-8 gap-y-4'}).find_all('a')
        chapters_urls = [link['href'].split('/')[-1] for link in links[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Omegascans.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Omegascans.send_request(f'https://omegascans.org/series/{manga}/{chapter['url']}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('p', {'class': 'flex flex-col justify-center items-center'})
        images = [image['src'] for image in images.find_all('img')]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        json = {'term': keyword}
        while True:
            mangas = Omegascans.send_request(f'https://api.omegascans.org/series/search', method='POST', json=json, wait=wait).json()
            results = {}
            if not mangas:
                yield results
            for manga in mangas:
                if absolute and keyword.lower() not in manga['title'].lower():
                    continue
                summary, type, alternative, chapters_count = '', '', '', ''
                with suppress(Exception): summary = manga['description']
                with suppress(Exception): type = manga['series_type']
                with suppress(Exception): alternative = manga['alternative_names']
                with suppress(Exception): chapters_count = manga['meta']['chapters_count']
                results[manga['title']] = {
                    'domain': Omegascans.domain,
                    'url': manga['series_slug'],
                    'thumbnail': manga['thumbnail'],
                    'summary': summary.replace('<p>', '').replace('</p>', ''),
                    'alternative': alternative,
                    'type': type,
                    'chapters_count': chapters_count,
                    'page': 1
                }
            yield results
            yield {}

    def get_db(wait=True):
        from contextlib import suppress
        statuses = ['Ongoing', 'Hiatus', 'Dropped', 'Completed']
        for status in statuses:
            page = 1
            total_pages = 1000
            while True:
                if page > total_pages:
                    yield {}
                response = Omegascans.send_request(f'https://api.omegascans.org/series/querysearch', method='POST', json={'series_status': status, 'page': page}, wait=wait).json()
                total_pages = response['meta']['total']
                mangas = response['data']
                results = {}
                for manga in mangas:
                    type, chapters_count, latest_chapter = '', '', ''
                    with suppress(Exception): type = manga['series_type']
                    with suppress(Exception): latest_chapter = manga['chapters'][0]['chapter_slug']
                    with suppress(Exception): chapters_count = manga['meta']['chapters_count']
                    results[manga['title']] = {
                        'domain': Omegascans.domain,
                        'url': manga['series_slug'],
                        'latest_chapter': latest_chapter,
                        'status': status,
                        'type': type,
                        'chapters_count': chapters_count,
                        'page': page
                    }
                yield results
                page += 1
        yield {}