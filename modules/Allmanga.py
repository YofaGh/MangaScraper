import json
from bs4 import BeautifulSoup
from utils.models import Manga

class Allmanga(Manga):
    domain = 'allmanga.to'
    logo = 'https://allanime.to/pics/icon-32x32.png'
    search_headers = {'if-none-match': '87272', 'Referer': 'https://allmanga.to/'}
    get_db_headers = {'Referer': 'https://allmanga.to/'}

    def get_chapters(manga):
        response = Allmanga.send_request(f'https://allmanga.to/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag: tag.name == 'script' and 'availableChaptersDetail' in tag.text).get_text(strip=True)
        inputs = script.split('function(', 1)[1].split(')')[0].split(',')
        outputs = script.rsplit('(', 1)[-1][:-3].replace('void ', '')
        outputs = json.loads(f'[{outputs}]')
        vars = dict(zip(inputs, outputs))
        chapters_urls = script.split('availableChaptersDetail:{', 1)[1].split('}')[0]
        subs, raws = [], []
        subs_raw = chapters_urls.split('sub:[', 1)[1].split(']')[0]
        subs_raw = [sub.replace('"', '') for sub in subs_raw.split(',')]
        for sub in subs_raw:
            if sub in vars:
                subs.append(vars[sub])
            else:
                subs.append(sub)
        raws_raw = chapters_urls.split('raw:[', 1)[1].split(']')[0]
        if raws_raw:
            raws_raw = [raw.replace('"', '') for raw in raws_raw.split(',')]
            raws = []
            for raw in raws_raw:
                if raw in vars:
                    raws.append(vars[raw])
                else:
                    raws.append(raw)
        chapters_urls = [f'chapter-{sub}-sub' for sub in subs[::-1]] + [f'chapter-{raw}-raw' for raw in raws[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Allmanga.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Allmanga.send_request(f'https://allmanga.to/read/{manga}/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag: tag.name == 'script' and 'selectedPicturesServer' in tag.text).get_text(strip=True)
        inputs = script.split('function(', 1)[1].split(')')[0].split(',')
        outputs = script.rsplit('(', 1)[-1][:-3].replace('void ', '')
        outputs = json.loads(f'[{outputs}]')
        vars = dict(zip(inputs, outputs))
        images = []
        images_raw = script.split('selectedPicturesServer:[', 1)[1].split(']')[0]
        for image in images_raw.split('},'):
            if image.split('url:')[1] in vars:
                images.append(vars[image.split('url:')[1]])
            else:
                images.append(image.split('url:"')[1].replace('"', '').replace('}', ''))
        images = [image.replace('\\u002F', '/') for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        query = '''https://api.allmanga.to/api?variables=
        {
            "search":{
                "query":"K_K_K_K","isManga":true},
                "limit":26,
                "page":P_P_P_P,
                "translationType":"sub",
                "countryOrigin":"ALL"
            }
            &extensions={
                "persistedQuery":{
                    "version":1,
                    "sha256Hash":"a27e57ef5de5bae714db701fb7b5cf57e13d57938fc6256f7d5c70a975d11f3d"
            }
        }'''
        page = 1
        while True:
            response = Allmanga.send_request(query.replace('P_P_P_P', str(page)).replace('K_K_K_K', keyword), headers=Allmanga.search_headers)
            mangas = response.json()['data']['mangas']['edges']
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                if absolute and keyword.lower() not in manga['name'].lower():
                    continue
                latest_chapter = ''
                if manga['lastChapterInfo']:
                    if manga['lastChapterInfo']['sub']:
                        latest_chapter = f'chapter-{manga["lastChapterInfo"]["sub"]["chapterString"]}-sub'
                    elif manga['lastChapterInfo']['raw']:
                        latest_chapter = f'chapter-{manga["lastChapterInfo"]["raw"]["chapterString"]}-raw'
                results[manga['name']] = {
                    'domain': Allmanga.domain,
                    'url': manga['_id'],
                    'latest_chapter': latest_chapter,
                    'thumbnail': f'https://wp.youtube-anime.com/aln.youtube-anime.com/{manga["thumbnail"]}',
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        from contextlib import suppress
        query = '''https://api.allmanga.to/api?variables=
        {
            "search":{
                "sortBy":"Name_ASC",
                "isManga":true
            },
            "limit":26,
            "page":P_P_P_P,
            "translationType":"sub",
            "countryOrigin":"ALL"
            }&extensions={
                "persistedQuery":{
                    "version":1,
                    "sha256Hash":"a27e57ef5de5bae714db701fb7b5cf57e13d57938fc6256f7d5c70a975d11f3d"
                }
        }'''
        page = 1
        while True:
            response = Allmanga.send_request(query.replace('P_P_P_P', str(page)), headers=Allmanga.get_db_headers)
            mangas = response.json()['data']['mangas']['edges']
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                latest_chapter = ''
                with suppress(Exception): latest_chapter = f'chapter-{manga["lastChapterInfo"]["sub"]["chapterString"]}-sub'
                results[manga['name']] = {
                    'domain': Allmanga.domain,
                    'url': manga['_id'],
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        tail = ' Raw' if 'raw' in chapter else ''
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
            return f'Chapter {int(new_name):03d}{tail}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}{tail}'