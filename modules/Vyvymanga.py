from bs4 import BeautifulSoup
from utils.models import Manga

class Vyvymanga(Manga):
    domain = 'vyvymanga.net'
    logo = 'https://vyvymanga.net/web/img/icon.png'

    def get_chapters(manga):
        response = Vyvymanga.send_request(f'https://vyvymanga.net/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        aas = soup.find_all('a', {'class': 'list-group-item list-group-item-action list-chapter'})
        chapters = [{
            'url': aa['href'],
            'name': aa.find('span').get_text(strip=True).replace(':', '_')
        } for aa in aas[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Vyvymanga.send_request(chapter['url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'vview carousel-inner'}).find_all('img')
        images = [image['data-src'] for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        while True:
            response = Vyvymanga.send_request(f'https://vyvymanga.net/search?q={keyword}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'comic-item'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'comic-title'}).get_text(strip=True)
                if absolute and keyword.lower() not in ti.lower():
                    continue
                latest_chapter, status = '', 'On Going'
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'tray-item'}).get_text(strip=True)
                with suppress(Exception): 
                    if manga.find('span', {'class': 'comic-completed'}): status = 'Completed'
                results[ti] = {
                    'domain': Vyvymanga.domain,
                    'url': manga.find('a')['href'].split('/')[-1],
                    'status': status,
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Vyvymanga.search_by_keyword('', False)

    @classmethod
    def download_image(cls, url, image_name, log_num, verify=None):
        from requests.exceptions import HTTPError
        from utils import logger
        try:
            response = cls.send_request(url, headers=cls.download_images_headers, verify=verify)
            image_format = response.headers['Content-Disposition'].split('.')[-1].replace('"', '')
            saved_path = f'{image_name}.{image_format}'
            with open(saved_path, 'wb') as image:
                image.write(response.content)
            return saved_path
        except HTTPError :
            logger.log(f' Warning: Could not download image {log_num}: {url}', 'red')
            return ''