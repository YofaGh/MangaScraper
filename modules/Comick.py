import json
from bs4 import BeautifulSoup
from utils.models import Manga
from user_agents import LEECH

class Comick(Manga):
    domain = 'comick.io'
    logo = 'https://comick.io/static/icons/unicorn-256_maskable.png'
    headers = {'Referer': 'https://comick.io/'}
    download_images_headers = headers

    def get_info(manga):
        response, _ = Comick.send_request(f'https://comick.io/comic/{manga}', headers=Comick.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = json.loads(soup.find('script', {'id': '__NEXT_DATA__'}).get_text(strip=True))['props']['pageProps']
        extras = {item['md_genres']['group']: [d['md_genres']['name'] for d in data['comic']['md_comic_md_genres'] if d.get('md_genres', {}).get('group') == item['md_genres']['group']] for item in data['comic']['md_comic_md_genres']}
        extras['Artinsts'] = [ti['name'] for ti in data['artists']]
        extras['Authors'] = [ti['name'] for ti in data['authors']]
        extras['demographic'] = data['demographic']
        extras['Published'] = data['comic']['year']
        extras['Publishers'] = [ti['mu_publishers']['title'] for ti in data['comic']['mu_comics']['mu_comic_publishers']]
        extras['Categories'] = [ti['mu_categories']['title'] for ti in data['comic']['mu_comics']['mu_comic_categories']]
        return {
            'Cover': f'https://meo3.comick.pictures/{data["comic"]["md_covers"][0]["b2key"]}',
            'Title': data['comic']['title'],
            'Alternative': ', '.join([ti['title'] for ti in data['comic']['md_titles']]),
            'Summary': data['comic']['desc'],
            'Rating': float(data['comic']['bayesian_rating'])/2,
            'Status': 'Ongoing' if data['comic']['status'] == 1 else 'Completed',
            'Extras': extras
        }

    def get_chapters(manga):
        response, session = Comick.send_request(f'https://comick.io/comic/{manga}', headers=Comick.headers)
        session.headers = Comick.headers
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        hid = json.loads(script.get_text(strip=True))['props']['pageProps']['comic']['hid']
        chapters_urls = []
        page = 1
        while True:
            response, session = Comick.send_request(f'https://api.comick.io/comic/{hid}/chapters?lang=en&chap-order=1&page={page}', session=session)
            response = response.json()
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
        response, _ = Comick.send_request(f'https://comick.io/comic/{manga}/{chapter["url"]}', headers=Comick.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        images = json.loads(script.get_text(strip=True))['props']['pageProps']['chapter']['md_images']
        images = [f'https://meo3.comick.pictures/{image["b2key"]}' for image in images]
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        response, session = Comick.send_request(f'https://comick.io/search', headers=Comick.headers)
        session.headers = Comick.headers
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'}).get_text(strip=True)
        genres = {genre['id']: genre['name'] for genre in json.loads(script)['props']['pageProps']['genres']}
        page = 1
        while True:
            try:
                response, session = Comick.send_request(f'https://api.comick.io/v1.0/search?q={keyword}&limit=300&page={page}', session=session)
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
                    'thumbnail': f'https://meo.comick.pictures/{manga["md_covers"][0]["b2key"]}' if manga['md_covers'] else '',
                    'genres': ', '.join([genres[genre_id] for genre_id in manga['genres']]),
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Comick.search_by_keyword('', False)

    def rename_chapter(chapter):
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
        new_name = new_name.rstrip('.')
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'