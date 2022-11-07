import requests
from bs4 import BeautifulSoup

class M_Manga:
    def get_chapters():
        return []

    def get_images():
        return []

    def search_by_title():
        return []

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return 'Chapter 000'
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number:
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'
        return rn(chapter)

class Manhuascan(M_Manga):
    def get_chapters(manga):
        response = requests.get(f'https://manhuascan.us/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'eph-num'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = requests.get(f'https://manhuascan.us/manga/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id': 'readerarea'}).find_all('img')
        images = [image['src'] for image in images]
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = requests.get(f'https://manhuascan.us/manga-list?search={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'bsx'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                results[manga.find('a')['href'].split('/')[-1]] = manga.find('a')['title']
            page += 1
        yield results
        return

class Skymanga(M_Manga):
    def get_chapters(manga):
        response = requests.get(f'https://skymanga.xyz/read/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = requests.get(f'https://skymanga.xyz/read/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class':'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = requests.get(f'https://skymanga.xyz/page/{page}/?s={title}&post_type=wp-manga')
            if response.status_code != 200:
                break
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            for manga in mangas:
                ti = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['title']
                link = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['href'].split('/')[-2]
                results[link] = ti
            page += 1
        yield results
        return

class Bibimanga(M_Manga):
    def get_chapters(manga):
        response = requests.get(f'https://bibimanga.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = requests.get(f'https://bibimanga.com/manga/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class':'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = requests.get(f'https://bibimanga.com/page/{page}?s={title}&post_type=wp-manga')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                ti = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['title']
                link = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['href'].split('/')[-2]
                results[link] = ti
            page += 1
        yield results
        return

class Manhwa18(M_Manga):
    def get_chapters(manga):
        response = requests.get(f'https://manhwa18.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        aas = soup.find('ul', {'class':'list-chapters at-series'}).find_all('a')
        chapters = [aa['href'].split('/')[-1] for aa in aas[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = requests.get(f'https://manhwa18.com/manga/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id':'chapter-content'}).find_all('img')
        images = [image['data-src'] for image in images]
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = requests.get(f'https://manhwa18.com/tim-kiem?q={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'thumb_attr series-title'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                results[manga.find('a')['href'].split('/')[-1]] = manga.find('a')['title']
            page += 1
        yield results
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
            elif ch in '-.' and reached_number:
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        new_name = new_name.rsplit('.', 1)[0]
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'

class Manhwa365(M_Manga):
    def get_chapters(manga):
        response = requests.get(f'https://manhwa365.com/webtoon/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = requests.get(f'https://manhwa365.com/webtoon/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class':'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = requests.get(f'https://manhwa365.com/page/{page}/?s={title}&post_type=wp-manga')
            if response.status_code != 200:
                break
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            for manga in mangas:
                ti = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['title']
                link = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['href'].split('/')[-2]
                results[link] = ti
            page += 1
        yield results
        return