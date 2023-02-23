import requests
from bs4 import BeautifulSoup

class Base():
    def send_request(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            if response.status_code == 404:
                raise Exception('Not found')
            elif response.status_code == 403:
                raise Exception('Forbidden')
            elif response.status_code == 500:
                raise Exception('Server Error')
            else:
                raise Exception
        except Exception as e:
            raise Exception(f'Connection error: {str(e)}')

class Base_Manga(Base):
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

class Readonepiece(Base_Manga):
    def get_chapters(*argv):
        response = Readonepiece.send_request('https://ww9.readonepiece.com/manga/one-piece-digital-colored-comics/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'bg-bg-secondary p-3 rounded mb-3 shadow'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        return chapters

    def get_images(*argv):
        response = Readonepiece.send_request(f'https://ww9.readonepiece.com/chapter/{argv[1]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', {'class', 'mb-3 mx-auto js-page'})
        images = [image['src'] for image in images]
        return images

class Manhuascan(Base_Manga):
    def get_chapters(manga):
        response = Manhuascan.send_request(f'https://manhuascan.us/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'eph-num'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manhuascan.send_request(f'https://manhuascan.us/manga/{manga}/{chapter}')
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
            response = Manhuascan.send_request(f'https://manhuascan.us/manga-list?search={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'bsx'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                results[manga.find('a')['href'].split('/')[-1]] = manga.find('a')['title']
            page += 1
        yield results
        return

class Skymanga(Base_Manga):
    def get_chapters(manga):
        response = Skymanga.send_request(f'https://skymanga.xyz/read/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Skymanga.send_request(f'https://skymanga.xyz/read/{manga}/{chapter}')
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
            response = Skymanga.send_request(f'https://skymanga.xyz/page/{page}/?s={title}&post_type=wp-manga')
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

class Bibimanga(Base_Manga):
    def get_chapters(manga):
        response = Bibimanga.send_request(f'https://bibimanga.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Bibimanga.send_request(f'https://bibimanga.com/manga/{manga}/{chapter}')
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
            response = Bibimanga.send_request(f'https://bibimanga.com/page/{page}?s={title}&post_type=wp-manga')
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

class Manhwa18(Base_Manga):
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
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = Manhwa18.send_request(f'https://manhwa18.com/tim-kiem?q={title}&page={page}')
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

class Manhwa365(Base_Manga):
    def get_chapters(manga):
        response = Manhwa365.send_request(f'https://manhwa365.com/webtoon/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manhwa365.send_request(f'https://manhwa365.com/webtoon/{manga}/{chapter}')
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
            response = Manhwa365.send_request(f'https://manhwa365.com/page/{page}/?s={title}&post_type=wp-manga')
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

class Truemanga(Base_Manga):
    def get_chapters(manga):
        response = Truemanga.send_request(f'https://truemanga.com/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('ul', {'class':'chapter-list'}).find_all('a')
        chapters = [link['href'].split('/')[-1] for link in links[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Truemanga.send_request(f'https://truemanga.com/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id':'chapter-images'}).find_all('img')
        images = [image['data-src'] for image in images]
        return images

    def search_by_title(title, limit_page=1000):
        results = {}
        page = 1
        while True:
            yield page
            if page > limit_page:
                break
            response = Truemanga.send_request(f'https://truemanga.com/search?q={title}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'book-item'})
            if len(mangas) == 0:
                break
            for manga in mangas:
                ti = manga.find('div', {'class': 'title'}).find('a')['title']
                link = manga.find('div', {'class': 'title'}).find('a')['href'].split('/')[-1]
                results[link] = ti
            page += 1
        yield results
        return