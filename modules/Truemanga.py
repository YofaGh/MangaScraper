from bs4 import BeautifulSoup
from utils.models import Manga

class Truemanga(Manga):
    domain = 'truemanga.com'
    download_images_headers = {'Referer': 'https://truemanga.com/'}

    def get_chapters(manga):
        response = Truemanga.send_request(f'https://truemanga.com/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('ul', {'class':'chapter-list'}).find_all('a')
        chapters = [link['href'].split('/')[-1] for link in links[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Truemanga.send_request(f'https://truemanga.com/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag:tag.name == 'script' and 'chapImages' in tag.text).text
        images = script.replace("var chapImages = '", '').strip()[:-1].split(',')
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        template = f'https://truemanga.com/search?q={keyword}&page=P_P_P_P' if keyword else 'https://truemanga.com/az-list?page=P_P_P_P'
        page = 1
        while True:
            try:
                response = Truemanga.send_request(template.replace('P_P_P_P', str(page)))
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'book-item'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'title'}).find('a')['title']
                if absolute and keyword.lower() not in ti.lower():
                    continue
                latest_chapter, genres, summary = '', '', ''
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'latest-chapter'})['title']
                with suppress(Exception): genres = manga.find('div', {'class': 'genres'}).get_text(strip=True, separator=', ')
                with suppress(Exception): summary = manga.find('div', {'class': 'summary'}).get_text(strip=True)
                results[ti] = {
                    'domain': Truemanga.domain,
                    'url': manga.find('div', {'class': 'title'}).find('a')['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'genres': genres,
                    'summary': summary,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Truemanga.search_by_keyword('', False)