from utils.models import Manga

class Mangadex(Manga):
    domain = 'mangadex.org'
    logo = 'https://mangadex.org/favicon.ico'

    def get_info(manga, wait=True):
        manga = manga.split('/')[0] if '/' in manga else manga
        response = Mangadex.send_request(f'https://api.mangadex.org/manga/{manga}?includes[]=artist&includes[]=author&includes[]=cover_art', wait=wait)
        data = response.json()['data']
        cover = next(filter(lambda x: x['type'] == 'cover_art', data['relationships']))['attributes']['fileName']
        return {
            'Cover': f'https://mangadex.org/covers/{manga}/{cover}',
            'Title': data['attributes']['title']['en'],
            'Alternative': ', '.join(list(g.values())[0] for g in data['attributes']['altTitles']),
            'Summary': data['attributes']['description']['en'],
            'Status': data['attributes']['status'],
            'Extras': {
                'Authors': [author['attributes']['name'] for author in data['relationships'] if author['type'] == 'author'],
                'Artists': [artist['attributes']['name'] for artist in data['relationships'] if artist['type'] == 'artist'],
                'Demographic': data['attributes']['publicationDemographic'],
                'Year': data['attributes']['year'],
                'Tags': [tag['attributes']['name']['en'] for tag in data['attributes']['tags'] if tag['type'] == 'tag']
            },
            'Dates': {
                'Created At': data['attributes']['createdAt'],
                'Updated At': data['attributes']['updatedAt']
            },
        }

    def get_chapters(manga, wait=True):
        manga = manga.split('/')[0] if '/' in manga else manga
        chapters = []
        params = {
            'limit': 500,
            'order[volume]': 'asc',
            'order[chapter]': 'asc',
            'offset': 0
        }
        while True:
            response = Mangadex.send_request(f'https://api.mangadex.org/manga/{manga}/feed', params=params, wait=wait).json()
            if len(response['data']) == 0:
                break
            chapters.extend([{
                'url': chapter['id'],
                'name': Mangadex.rename_chapter(chapter['attributes']['chapter'])
            } for chapter in response['data'] if chapter['attributes']['pages'] and chapter['attributes']['translatedLanguage'] == 'en'])
            params['offset'] += 500
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Mangadex.send_request(f'https://api.mangadex.org/at-home/server/{chapter["url"]}', wait=wait).json()
        images = [f'{response["baseUrl"]}/data/{response["chapter"]["hash"]}/{image}' for image in response['chapter']['data']]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        page = 1
        params = {'limit': 100, 'title': keyword, 'order[relevance]': 'desc', 'includes[]': 'cover_art'} if keyword else {'limit': 100, 'order[title]': 'asc'}
        url = 'https://api.mangadex.org/manga'
        while True:
            params['offset'] = (page - 1) * 100
            try:
                response = Mangadex.send_request(url, params=params, wait=wait).json()
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
                cover = ''
                try:
                    for relationship in manga['relationships']:
                        if relationship['type'] == 'cover_art':
                            cover = f'https://mangadex.org/covers/{manga["id"]}/{relationship["attributes"]["fileName"]}'
                            break
                except: pass
                results[title] = {
                    'domain': Mangadex.domain,
                    'url': manga['id'],
                    'summary': summary.get('en') or summary[list(summary)[0]],
                    'original_language': manga['attributes']['originalLanguage'],
                    'latest_chapter': manga['attributes']['lastChapter'],
                    'latest_volume': manga['attributes']['lastVolume'],
                    'thumbnail': cover,
                    'status': manga['attributes']['status'],
                    'tags': ', '.join([tag['attributes']['name']['en'] for tag in manga['attributes']['tags']]),
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Mangadex.search_by_keyword('', False, wait=wait)