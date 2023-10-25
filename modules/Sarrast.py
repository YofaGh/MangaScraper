from bs4 import BeautifulSoup
from utils.models import Manga

class Sarrast(Manga):
    domain = 'sarrast.com'

    def get_chapters(manga, wait=True):
        response = Sarrast.send_request(f'https://sarrast.com/series/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('div', {'class': 'text-white mb-20 mt-8 relative px-4'}).find_all('a')
        chapters_urls = [div['href'].split('/')[-1] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Sarrast.rename_chapter(chapter_url.rsplit('-', 1)[0])
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Sarrast.send_request(f'https://sarrast.com/series/{manga}/{chapter["url"]}/api', wait=wait).json()
        images = [f'https://sarrast.com{image["path"]}' for image in response['files']]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        try:
            response = Sarrast.send_request(f'https://sarrast.com/search?value={keyword}', wait=wait)
            mangas = response.json()
            results = {}
            if not mangas:
                yield results
            for manga in mangas:
                results[manga['title']] = {
                    'domain': Sarrast.domain,
                    'url': manga['slug'],
                    'thumbnail': ''
                }
            yield results
        except HTTPError:
            yield {}
        yield {}

    def get_db(wait=True):
        return Sarrast.search_by_keyword('', False, wait=wait)