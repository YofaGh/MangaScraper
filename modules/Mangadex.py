from utils.models import Manga

class Mangadex(Manga):
    domain = 'mangadex.org'

    def get_chapters(manga):
        manga = manga.split('/')[0] if '/' in manga else manga
        chapters = []
        params = {
            'limit': 500,
            'order[volume]': 'asc',
            'order[chapter]': 'asc',
            'offset': 0
        }
        while True:
            response = Mangadex.send_request(f'https://api.mangadex.org/manga/{manga}/feed', params=params).json()
            if len(response['data']) == 0:
                break
            chapters.extend([{
                'url': chapter['id'],
                'name': Mangadex.rename_chapter(chapter['attributes']['chapter'])
            } for chapter in response['data'] if chapter['attributes']['pages'] and chapter['attributes']['translatedLanguage'] == 'en'])
            params['offset'] += 500
        return chapters

    def get_images(manga, chapter):
        response = Mangadex.send_request(f'https://api.mangadex.org/at-home/server/{chapter["url"]}').json()
        images = [f'{response["baseUrl"]}/data/{response["chapter"]["hash"]}/{image}' for image in response['chapter']['data']]
        return images, False

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        page = 1
        params = {'limit': 100, 'title': keyword, 'order[relevance]': 'desc'} if keyword else {'limit': 100, 'order[title]': 'asc'}
        url = 'https://api.mangadex.org/manga'
        while True:
            params['offset'] = (page - 1) * 100
            try:
                response = Mangadex.send_request(url, params=params).json()
            except HTTPError:
                yield {}
            mangas = response['data']
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga['attributes']['title']
                title = ti.get('en', ti[list(ti)[0]])
                if absolute and keyword.lower() not in title.lower():
                    continue
                summary = manga['attributes']['description'] or {'en': ''}
                results[title] = {
                    'domain': Mangadex.domain,
                    'url': manga['id'],
                    'summary': summary.get('en') or summary[list(summary)[0]],
                    'original_language': manga['attributes']['originalLanguage'],
                    'latest_chapter': manga['attributes']['lastChapter'],
                    'latest_volume': manga['attributes']['lastVolume'],
                    'status': manga['attributes']['status'],
                    'tags': ', '.join([tag['attributes']['name']['en'] for tag in manga['attributes']['tags']]),
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Mangadex.search_by_keyword('', False)