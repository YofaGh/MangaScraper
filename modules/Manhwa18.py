from bs4 import BeautifulSoup
from utils.models import Manga

class Manhwa18(Manga):
    domain = 'manhwa18.com'

    def get_chapters(manga):
        response = Manhwa18.send_request(f'https://manhwa18.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        aas = soup.find('ul', {'class':'list-chapters at-series'}).find_all('a')
        chapters = [aa['href'].split('/')[-1] for aa in aas[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manhwa18.send_request(f'https://manhwa18.com/manga/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id':'chapter-content'}).find_all('img')
        images = [image['data-src'] for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Manhwa18.send_request(f'https://manhwa18.com/tim-kiem?q={keyword}&page={page}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'thumb-item-flow col-6 col-md-2'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'thumb_attr series-title'}).find('a')['title']
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    'domain': Manhwa18.domain,
                    'url': manga.find('a')['href'].split('/')[-1],
                    'latest_chapter': manga.find('div', {'class': 'thumb-detail'}).find('a')['href'].split('/')[-1],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manhwa18.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
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
        new_name = new_name.rsplit('.', 1)[0]
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'