from bs4 import BeautifulSoup
from utils.models import Manga

class Manga18hot(Manga):
    domain = 'manga18hot.net'

    def get_chapters(manga):
        manga = manga.replace('manga-', '') if manga.startswith('manga-') else manga
        response = Manga18hot.send_request(f'https://manga18hot.net/manga-{manga}.html')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'class': 'item-link'})
        return [link['href'].replace(f'read-{manga}-', '').replace('.html', '') for link in links[::-1]]

    def get_images(manga, chapter):
        manga = manga.replace('manga-', '') if manga.startswith('manga-') else manga
        response = Manga18hot.send_request(f'https://manga18hot.net/read-{manga}-{chapter}.html')
        soup = BeautifulSoup(response.text, 'html.parser')
        chapter_id = soup.find('body').find('div')['data-reading-id']
        response = Manga18hot.send_request(f'https://manga18hot.net/app/manga/controllers/cont.getChapter.php?chapter={chapter_id}&mode=vertical&quality=high').json()
        soup = BeautifulSoup(response['html'], 'html.parser')
        divs = soup.find_all('div', {'class': 'iv-card shuffled'})
        images = [div['data-url'].strip() for div in divs]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        prev_page = []
        while True:
            try:
                response = Manga18hot.send_request(f'https://manga18hot.net/manga-list.html?page={page}&name={keyword}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'item item-spc'})
            results = {}
            if prev_page == mangas:
                yield {}
            for manga in mangas:
                ti = manga.find('h3', {'class': 'manga-name'}).find('a')
                if absolute and keyword.lower() not in ti['title'].lower():
                    continue
                url = ti['href'].replace('manga-', '').replace('.html', '')
                latest_chapter, genres = '', ''
                with suppress(Exception): genres = manga.find('span', {'class': 'fdi-item fdi-cate'}).get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('div', {'class': 'fd-list'}).find('a')['href'].split('/')[-1]
                results[ti['title']] = {
                    'domain': Manga18hot.domain,
                    'url': f'manga-{url}',
                    'latest_chapter': latest_chapter.replace(f'read-{url}-', '').replace('.html', ''),
                    'genres': genres,
                    'page': page
                }
            yield results
            prev_page = mangas
            page += 1

    def get_db():
        return Manga18hot.search_by_keyword('', False)