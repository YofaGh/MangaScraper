from utils.Bases import Manga, Req
from bs4 import BeautifulSoup

class Manhwa18(Manga, Req):
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

    def search(title, sleep_time, absolute=False, limit_page=1000):
        import time
        results = []
        page = 1
        while page <= limit_page:
            yield False, page
            response = Manhwa18.send_request(f'https://manhwa18.com/tim-kiem?q={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'thumb_attr series-title'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                if absolute and title.lower() not in manga.find('a')['title'].lower():
                    continue
                results.append(f'title: {manga.find("a")["href"].split("/")[-1]}, url: {manga.find("a")["title"]}')
            page += 1
            time.sleep(sleep_time)
        yield True, results
        return

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return 'Chapter 000'
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