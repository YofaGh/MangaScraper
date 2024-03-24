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
        images = [item for item in data if isinstance(item, str) and '/comic/' in item]
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        page = 1
        while True:
            response = Mangapark.send_request(f'https://mangapark.to/search?word={keyword}&page={page}', wait=wait)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'flex border-b border-b-base-200 pb-5'})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                name = manga.find('h3').get_text(strip=True)
                url = manga.find('h3').find('a')['href'].split('/')[-1]
                authors, alternatives, genres, latest_chapter = '', '', '', ''
                with suppress(Exception): authors = ', '.join(manga.find('div', {'q:key': '6N_0'}).get_text(strip=True).split('/'))
                with suppress(Exception): alternatives = ', '.join(manga.find('div', {'q:key': 'lA_0'}).get_text(strip=True).split('/'))
                with suppress(Exception): genres = ', '.join(manga.find('div', {'q:key': 'HB_9'}).get_text(strip=True).split(','))
                with suppress(Exception): latest_chapter = manga.find('div', {'q:key': 'R7_8'}).find('a')['href'].split('/')[-1]
                if absolute and keyword.lower() not in name.lower():
                    continue
                results[name] = {
                    'domain': Mangapark.domain,
                    'url': url,
                    'thumbnail': manga.find('img')['src'],
                    'alternatives': alternatives,
                    'authors': authors,
                    'genres': genres,
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Mangapark.search_by_keyword('', False, wait=wait)