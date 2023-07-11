from bs4 import BeautifulSoup
from utils.models import Manga

class Manga18(Manga):
    domain = 'manga18.club'
    headers = {'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)'}

    def get_chapters(manga):
        response = Manga18.send_request(f'https://manga18.club/manhwa/{manga}', headers=Manga18.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find('div', {'class': 'chapter_box'}).find_all('li')
        chapters = [li.find('a')['href'].split('/')[-1] for li in lis[::-1]]
        return chapters

    def get_images(manga, chapter):
        import base64
        response = Manga18.send_request(f'https://manga18.club/manhwa/{manga}/{chapter}', headers=Manga18.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag:tag.name == 'script' and 'slides_p_path' in tag.text)
        images = script.text.split('[', 1)[1].split(']', 1)[0][:-1]
        images = [image.replace('"', '') for image in images.split(',')]
        images = [base64.b64decode(image).decode('utf-8') for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        while True:
            response = Manga18.send_request(f'https://manga18.club/list-manga/{page}?search={keyword}', headers=Manga18.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'col-md-3 col-sm-4 col-xs-6'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'mg_name'}).find('a')
                if absolute and keyword.lower() not in ti.contents[0].lower():
                    continue
                latest_chapter = ''
                with suppress(Exception): latest_chapter = manga.find('div', {'class': 'mg_chapter'}).find('a')['href'].split('/')[-1]
                results[ti.contents[0]] = {
                    'domain': Manga18.domain,
                    'url': ti['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manga18.search_by_keyword('', False)