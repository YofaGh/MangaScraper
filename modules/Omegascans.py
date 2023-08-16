from bs4 import BeautifulSoup
from utils.models import Manga

class Omegascans(Manga):
    domain = 'omegascans.org'

    def get_chapters(manga):
        response = Omegascans.send_request(f'https://omegascans.org/series/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('div', {'class': 'chapters-list-wrapper'}).find_all('a')
        chapters_urls = [link['href'].split('/')[-1] for link in links[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Omegascans.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        import json
        response = Omegascans.send_request(f'https://omegascans.org/series/{manga}/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        id = json.loads(script.text)['props']['pageProps']['data']['id']
        response = Omegascans.send_request(f'https://api.omegascans.org/series/chapter/{id}')
        images = []
        for image in response.json()['content']['images']:
            images.append(image if 'https://' in image else f'https://api.omegascans.org/{image}')
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        json = {'term': keyword}
        while True:
            mangas = Omegascans.send_request(f'https://api.omegascans.org/series/search', method='POST', json=json).json()
            results = {}
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
                    'summary': summary.replace('<p>', '').replace('</p>', ''),
                    'alternative': alternative,
                    'type': type,
                    'chapters_count': chapters_count,
                    'page': 1
                }
            yield results
            yield {}

    def get_db():
        from contextlib import suppress
        statuses = ['Ongoing', 'Hiatus', 'Dropped', 'Completed']
        for status in statuses:
            page = 1
            total_pages = 1000
            while True:
                if page > total_pages:
                    yield {}
                response = Omegascans.send_request(f'https://api.omegascans.org/series/querysearch', method='POST', json={'series_status': status, 'page': page}).json()
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