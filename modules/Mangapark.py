from bs4 import BeautifulSoup
from utils.models import Manga

class Mangapark(Manga):
    domain = 'mangapark.to'
    logo = 'https://mangapark.to/public-assets/img/favicon.ico'

    def get_info(manga, wait=True):
        import json
        manga = manga.split('-')[0] if '-' in manga else manga
        response = Mangapark.send_request(f'https://mangapark.to/title/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'}).get_text(strip=True)
        data = json.loads(script)['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['data']
        return {
            'Cover': data['urlCover600'],
            'Title': data['name'],
            'Alternative': ', '.join(data['altNames']) if data['altNames'] else '',
            'Summary': data['summary']['code'] if data['summary'] else '',
            'Rating': data['stat_score_avg'] if data['stat_score_avg'] else '',
            'Status': data['originalStatus'] if data['originalStatus'] else '',
            'Extras': {
                'Authors': data['authors'] if data['authors'] else '',
                'Artists': data['artists'] if data['artists'] else '',
                'Genres': data['genres'] if data['genres'] else '',
            },
        }

    def get_chapters(manga, wait=True):
        import json
        response = Mangapark.send_request(f'https://mangapark.to/title/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'type': 'qwik/json'}).text
        data = json.loads(script)['objs']
        chapters = [{
            'url': item.split('/')[-1],
            'name': Mangapark.rename_chapter(str(data[i-1]))
        } for i, item in enumerate(data) if isinstance(item, str) and f'{manga}/' in item]
        return chapters

    def get_images(manga, chapter, wait=True):
        import json
        response = Mangapark.send_request(f'https://mangapark.to/title/{manga}/{chapter["url"]}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'type': 'qwik/json'})
        data = json.loads(script.text)['objs']
        images = [item for item in data if isinstance(item, str) and 'comic' in item and '?acc=' in item]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        page = 1
        prev_page = {}
        while True:
            data_json = {
                'query':'''query get_content_browse_search($select: ComicSearchSelect) { get_content_browse_search( select: $select ) {
                    items { data {name authors artists genres originalStatus summary { code } urlPath urlCover600 } max_chapterNode { data { urlPath } } } } }''',
                'variables': {
                    'select': {
                        'word': keyword,
                        'page': page
                    }
                },
                'operationName':'get_content_browse_search'
            }
            response = Mangapark.send_request('https://mangapark.to/apo/', method='POST', headers={'content-type': 'application/json'}, json=data_json, wait=wait).json()
            mangas = response['data']['get_content_browse_search']['items']
            if mangas == prev_page:
                yield {}
            results = {}
            for manga in mangas:
                name = manga['data']['name']
                url = manga['data']['urlPath'].split('/')[-1]
                authors, artists, genres, status, summary, latest_chapter = '', '', '', '', '', ''
                with suppress(Exception): authors = ', '.join(manga['data']['authors'])
                with suppress(Exception): artists = ', '.join(manga['data']['artists'])
                with suppress(Exception): genres = ', '.join(manga['data']['genres'])
                with suppress(Exception): status = manga['data']['originalStatus']
                with suppress(Exception): summary = manga['data']['summary']['code']
                with suppress(Exception): latest_chapter = manga['max_chapterNode']['data']['urlPath'].split('/')[-1]
                if absolute and keyword.lower() not in name.lower():
                    continue
                results[name] = {
                    'domain': Mangapark.domain,
                    'url': url,
                    'thumbnail': manga['data']['urlCover600'],
                    'authors': authors,
                    'artists': artists,
                    'genres': genres,
                    'status': status,
                    'summary': summary,
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1
            prev_page = mangas

    def get_db(wait=True):
        return Mangapark.search_by_keyword('', False, wait=wait)