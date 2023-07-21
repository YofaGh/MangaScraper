from bs4 import BeautifulSoup
from utils.models import Manga

class Mangapark(Manga):
    domain = 'mangapark.to'

    def get_chapters(manga):
        manga = manga.split('-')[0] if '-' in manga else manga
        data_json = {
            'query': '''query get_chapters($select: Content_ComicChapterRangeList_Select) 
            { get_content_comicChapterRangeList( select: $select ) { pager {x y} } } ''',
            'variables': {
                'select': { 'comicId': manga }
            },
            'operationName': 'get_chapters'
        }
        response = Mangapark.send_request('https://mangapark.to/apo/', method='POST', headers={'content-type': 'application/json'}, json=data_json).json()
        end = response['data']['get_content_comicChapterRangeList']['pager'][0]['x']
        begin = response['data']['get_content_comicChapterRangeList']['pager'][-1]['y']
        data_json['variables']['select']['range'] = {'x': begin, 'y': end}
        data_json['query'] = '''query get_chapters($select: Content_ComicChapterRangeList_Select) 
            { get_content_comicChapterRangeList( select: $select ) { items{ chapterNodes { data {urlPath} } } } } '''
        response = Mangapark.send_request('https://mangapark.to/apo/', method='POST', headers={'content-type': 'application/json'}, json=data_json).json()
        items = response['data']['get_content_comicChapterRangeList']['items']
        chapters = [item['chapterNodes'][0]['data']['urlPath'].split('/')[-1] for item in items[::-1]]
        return chapters

    def get_images(manga, chapter):
        import json
        response = Mangapark.send_request(f'https://mangapark.to/title/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        data = json.loads(script.text)
        images_raw = data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['data']['imageSet']
        images = [f'{url}?{tail}' for url, tail in zip(images_raw['httpLis'], images_raw['wordLis'])]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        prev_page = {}
        while True:
            data_json = {
                'query':'''query get_content_browse_search($select: ComicSearchSelect) { get_content_browse_search( select: $select ) {
                    items { data {name authors artists genres originalStatus summary { code } urlPath } max_chapterNode { data { urlPath } } } } }''',
                'variables': {
                    'select': {
                        'word': keyword,
                        'page': page
                    }
                },
                'operationName':'get_content_browse_search'
            }
            response = Mangapark.send_request('https://mangapark.to/apo/', method='POST', headers={'content-type': 'application/json'}, json=data_json).json()
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

    def get_db():
        return Mangapark.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        chapter = chapter.split('-')[-1]
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'