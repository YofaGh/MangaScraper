from bs4 import BeautifulSoup
from utils.models import Manga

class Comics8Muses(Manga):
    domain = 'comics.8muses.com'

    def get_chapters(manga):
        page = 1
        chapters = []
        response = Comics8Muses.send_request(f'https://comics.8muses.com/comics/album/{manga}/{page}')
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.find('div', {'class':'image-title'}):
            return ['']
        while True:
            links = soup.find_all('a', {'class': 'c-tile t-hover'}, href=True)
            if not links:
                break
            chapters += [link.get('href').split('/')[-1] for link in links]
            page += 1
            response = Comics8Muses.send_request(f'https://comics.8muses.com/comics/album/{manga}/{page}')
            soup = BeautifulSoup(response.text, 'html.parser')
        return chapters

    def get_images(manga, chapter):
        response = Comics8Muses.send_request(f'https://comics.8muses.com/comics/album/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'class': 'c-tile t-hover'})
        images = [link.find('img').get('data-src') for link in links]
        images = [f'https://comics.8muses.com/image/fm/{image.split("/")[-1]}' for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        page = 1
        links = []
        while True:
            response = Comics8Muses.send_request(f'https://comics.8muses.com/search?q={keyword}&page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            comics = soup.find_all('a', {'class': 'c-tile t-hover'}, href=True)
            results = {}
            if not comics:
                yield {}
            for comic in comics:
                if not comic.get('href'):
                    continue
                if absolute and keyword.lower() not in comic.get_text(strip=True).lower():
                    continue
                url = comic.get('href').replace('https://comics.8muses.com/comics/album/', '')
                sublink = False
                for link in links:
                    if link in url:
                        sublink = True
                        break
                if not sublink:
                    links.append(url)
                    results[comic.get_text(strip=True)] = {
                        'domain': Comics8Muses.domain,
                        'url': url,
                        'page': page
                    }
            yield results
            page += 1

    def get_db():
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Comics8Muses.send_request(f'https://comics.8muses.com/sitemap/{page}.xml')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'xml')
            results = {}
            urls = soup.find_all('loc')
            for url in urls:
                results[url.get_text().split('/')[-1].replace('-', ' ')] = {
                    'domain': Comics8Muses.domain,
                    'url': url.get_text().replace('https://comics.8muses.com/comics/album/', ''),
                    'page': page
                }
            yield results
            page += 1

    def rename_chapter(name):
        return name.replace('-', ' ')