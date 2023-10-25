from bs4 import BeautifulSoup
from utils.models import Manga

class Comics8Muses(Manga):
    domain = 'comics.8muses.com'
    logo = 'https://comics.8muses.com/favicon.ico'

    def get_chapters(manga, wait=True):
        page = 1
        chapters_urls = []
        response = Comics8Muses.send_request(f'https://comics.8muses.com/comics/album/{manga}/{page}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.find('div', {'class':'image-title'}):
            return ['']
        while True:
            links = soup.find_all('a', {'class': 'c-tile t-hover'}, href=True)
            if not links:
                break
            chapters_urls += [link.get('href').split('/')[-1] for link in links]
            page += 1
            response = Comics8Muses.send_request(f'https://comics.8muses.com/comics/album/{manga}/{page}', wait=wait)
            soup = BeautifulSoup(response.text, 'html.parser')
        chapters = [{
            'url': chapter_url,
            'name': Comics8Muses.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Comics8Muses.send_request(f'https://comics.8muses.com/comics/album/{manga}/{chapter["url"]}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'class': 'c-tile t-hover'})
        images = [link.find('img').get('data-src') for link in links]
        images = [f'https://comics.8muses.com/image/fm/{image.split("/")[-1]}' for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        page = 1
        links = []
        while True:
            response = Comics8Muses.send_request(f'https://comics.8muses.com/search?q={keyword}&page={page}', wait=wait)
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
                        'thumbnail': f'https://comics.8muses.com{comic.find("img")["data-src"]}',
                        'page': page
                    }
            yield results
            page += 1

    def get_db(wait=True):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Comics8Muses.send_request(f'https://comics.8muses.com/sitemap/{page}.xml', wait=wait)
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