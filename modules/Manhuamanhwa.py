from bs4 import BeautifulSoup
from utils.models import Manga

class Manhuamanhwa(Manga):
    domain = 'manhuamanhwa.com'
    headers = {
        'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)',
        "Referer": "https://manhuamanhwa.com/"
    }

    def get_chapters(manga):
        response = Manhuamanhwa.send_request(f'https://manhuamanhwa.com/manga/{manga}/ajax/chapters/', method='POST', headers=Manhuamanhwa.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manhuamanhwa.send_request(f'https://manhuamanhwa.com/manga/{manga}/{chapter}/', headers=Manhuamanhwa.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['data-src'] for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Manhuamanhwa.send_request(f'https://manhuamanhwa.com/page/{page}?s={keyword}&post_type=wp-manga', headers=Manhuamanhwa.headers)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['title']
                if absolute and keyword.lower() not in ti.lower():
                    continue
                link = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['href'].split('/')[-2]
                latest_chapter, genres, authors, artists, status = '', '', '', '', ''
                contents = manga.find_all('div', {'class': 'post-content_item'})
                for content in contents:
                    with suppress(Exception):
                        head = content.find('h5').contents[0].replace('\n', '').replace(' ', '')
                        if head == 'Authors':
                            authors = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Artists':
                            artists = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Genres':
                            genres = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Status':
                            status = content.find('div', {'class': 'summary-content'}).contents[0].replace('\n', '').replace(' ', '')
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[ti] = {
                    'domain': Manhuamanhwa.domain,
                    'url': link,
                    'latest_chapter': latest_chapter,
                    'genres': genres,
                    'authors': authors,
                    'artists': artists,
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manhuamanhwa.search_by_keyword('', False)

    def download_image(url, image_name, log_num):
        import requests
        from termcolor import colored
        from utils.assets import waiter
        while True:
            try:
                response = requests.get(url, headers=Manhuamanhwa.headers)
                response.raise_for_status()
                with open(image_name, 'wb') as image:
                    image.write(response.content)
                return image_name
            except (requests.exceptions.HTTPError) as error:
                print(colored(f' Warning: Could not download image {log_num}: {url}', 'red'))
                return ''
            except (requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                waiter()