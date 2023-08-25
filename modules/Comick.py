import json
from bs4 import BeautifulSoup
from utils.models import Manga

class Comick(Manga):
    domain = 'comick.app'
    logo = 'https://comick.app/static/icons/unicorn-256_maskable.png'
    headers = {'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)'}
    download_images_headers = {'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)'}

    def get_chapters(manga):
        response = Comick.send_request(f'https://comick.app/comic/{manga}', headers=Comick.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        hid = json.loads(script.get_text(strip=True))['props']['pageProps']['comic']['hid']
        chapters_urls = []
        page = 1
        while True:
            response = Comick.send_request(f'https://api.comick.app/comic/{hid}/chapters?lang=en&chap-order=1&page={page}', headers=Comick.headers).json()
            if not response['chapters']:
                break
            chapters_urls.extend([f'{chapter["hid"]}-chapter-{chapter["chap"]}-en' for chapter in response['chapters'] if chapter['chap']])
            page += 1
        chapters = [{
            'url': chapter_url,
            'name': Comick.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Comick.send_request(f'https://comick.app/comic/{manga}/{chapter["url"]}', headers=Comick.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        images = json.loads(script.get_text(strip=True))['props']['pageProps']['chapter']['md_images']
        images = [f'https://meo3.comick.pictures/{image["b2key"]}' for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        response = Comick.send_request(f'https://comick.app/search', headers=Comick.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'}).get_text(strip=True)
        genres = {genre['id']: genre['name'] for genre in json.loads(script)['props']['pageProps']['genres']}
        page = 1
        while True:
            try:
                response = Comick.send_request(f'https://api.comick.app/v1.0/search?q={keyword}&limit=300&page={page}', headers=Comick.headers)
            except HTTPError:
                yield {}
            mangas = response.json()
            results = {}
            for manga in mangas:
                if absolute and keyword.lower() not in manga['title'].lower():
                    continue
                results[manga['title']] = {
                    'domain': Comick.domain,
                    'url': manga['slug'],
                    'latest_chapter': manga['last_chapter'],
                    'genres': ', '.join([genres[genre_id] for genre_id in manga['genres']]),
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Comick.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        chapter = chapter.split('-', 1)[1]
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