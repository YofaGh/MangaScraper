from bs4 import BeautifulSoup
from utils.models import Manga

class Omegascans(Manga):
    domain = 'omegascans.org'
    logo = 'https://omegascans.org/icon.png'

    def get_info(manga):
        from contextlib import suppress
        from urllib.parse import unquote
        response = Omegascans.send_request(f'https://omegascans.org/series/{manga}')
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

    def get_chapters(manga):
        session = Omegascans.create_session()
        response = Omegascans.send_request('https://omegascans.org/series/where-is-my-hammer', session=session)
        soup = BeautifulSoup(response.text, 'html.parser')
        series_id = soup.find(lambda tag: tag.name == 'script' and 'series_id' in tag.text).text.split('{\\"series_id\\":')[1].split(',')[0]
        response = Omegascans.send_request(f'https://api.omegascans.org/chapter/query?page=1&perPage=10000&series_id={series_id}', session=session)
        chapters = [{
            'url': chapter['chapter_slug'],
            'name': chapter['chapter_name']
        } for chapter in response.json()['data'][::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Omegascans.send_request(f'https://omegascans.org/series/{manga}/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('p', {'class': 'flex flex-col justify-center items-center'})
        images = [image['src'] for image in images.find_all('img')]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        data = {'adult': 'true', 'query_string': keyword, 'page': 1}
        while True:
            mangas = Omegascans.send_request(f'https://api.omegascans.org/query', params=data).json()['data']
            results = {}
            if not mangas:
                yield results
            for manga in mangas:
                if absolute and keyword.lower() not in manga['title'].lower():
                    continue
                summary, type, alternative, chapters_count, latest_chapter = '', '', '', '', ''
                with suppress(Exception): summary = manga['description']
                with suppress(Exception): type = manga['series_type']
                with suppress(Exception): alternative = manga['alternative_names']
                with suppress(Exception): chapters_count = manga['meta']['chapters_count']
                with suppress(Exception): latest_chapter = manga['latest_chapter']['chapter_slug']
                results[manga['title']] = {
                    'domain': Omegascans.domain,
                    'url': manga['series_slug'],
                    'thumbnail': manga['thumbnail'],
                    'summary': summary.replace('<p>', '').replace('</p>', ''),
                    'alternative': alternative,
                    'type': type,
                    'chapters_count': chapters_count,
                    'latest_chapter': latest_chapter,
                    'page': data['page']
                }
            yield results
            data['page'] += 1

    def get_db():
        return Omegascans.search_by_keyword('', False)