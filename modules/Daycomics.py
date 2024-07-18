from bs4 import BeautifulSoup
from utils.models import Manga

class Daycomics(Manga):
    domain = 'daycomics.me'
    logo = 'https://static.daycomics.me/hc-cdn/5de41062bd2fd10a10781a1059d47548e49.png'
    headers = {'cookie': 'hc_vfs=Y'}
    download_images_headers = {'Referer': 'https://daycomics.me'}

    def get_info(manga):
        from contextlib import suppress
        manga = manga[:-5] if manga.endswith('.html') else manga
        manga = manga.replace('https://daycomics.me/en/', '')
        response, _ = Daycomics.send_request(f'https://daycomics.me/en/{manga}.html', headers=Daycomics.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, summary = '', '', ''
        info_box = soup.find('div', {'class': 'inner_ch'})
        extras = {}
        with suppress(Exception): cover = info_box['style'].split("url('")[1].split("')")[0]
        with suppress(Exception): title = info_box.find('h2', {'class': 'episode-title'}).get_text(strip=True)
        with suppress(Exception): summary = info_box.find('div', {'class': 'title_content'}).find_all('h2')[-1].get_text(strip=True)
        with suppress(Exception): extras['Genres'] = [genre.strip() for genre in info_box.find('p', {'class': 'type_box'}).find('span', {'class': 'type'}).get_text(strip=True).split(' / ')]
        with suppress(Exception): extras['Authors'] = info_box.find('p', {'class': 'type_box'}).find('span', {'class': 'writer'}).get_text(strip=True)
        return {
            'Cover': cover,
            'Title': title,
            'Summary': summary,
            'Extras': extras,
        }

    def get_chapters(manga):
        manga = manga[:-5] if manga.endswith('.html') else manga
        manga = manga.replace('https://daycomics.me/en/', '')
        response, _ = Daycomics.send_request(f'https://daycomics.me/en/{manga}.html', headers=Daycomics.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find_all('li', {'class': 'normal_ep'})
        chapters = [{
            'url': li.find('a')['href'],
            'name': Manga.rename_chapter(li.find('span', {'class': 'num'}).get_text(strip=True))
        } for li in lis]
        return chapters

    def get_images(manga, chapter):
        manga = manga[:-5] if manga.endswith('.html') else manga
        chapter["url"] = chapter["url"][:-5] if chapter["url"].endswith('.html') else chapter["url"]
        chapter["url"] = chapter["url"].replace('https://daycomics.me/en/', '')
        response, _ = Daycomics.send_request(f'https://daycomics.me/en/{chapter["url"]}.html', headers=Daycomics.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('div', {'class': 'viewer-imgs'}).find_all('img')
        images = [div['data-src'].strip() if div.has_attr('data-src') else div['src'].strip() for div in divs]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        session = None
        template = f'https://daycomics.me/en/search?keyword={keyword}&' if keyword else 'https://daycomics.me/en/genres?'
        while True:
            response, session = Daycomics.send_request(f'{template}page={page}', headers=Daycomics.headers, session=session)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('li', {'itemtype': 'https://schema.org/ComicSeries'})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('h4', {'class': 'title'}).get_text(strip=True)
                if absolute and keyword.lower() not in ti.lower():
                    continue
                status, authors, genres = '', '', ''
                with suppress(Exception): status = 'Finished' if 'End' in manga.find('p', {'class': 'ico-box'}).get_text(strip=True) else 'Ongoing'
                with suppress(Exception): authors = manga.find('p', {'class': 'writer'}).get_text(strip=True)
                with suppress(Exception): genres = [genre.get_text(strip=True) for genre in manga.find('p', {'class': 'etc'}).find_all('span')]
                results[ti] = {
                    'domain': Daycomics.domain,
                    'url': manga.find('a')['href'].replace('https://daycomics.me/en/', '')[:-5],
                    'thumbnail': manga.find('img')['src'],
                    'status': status,
                    'authors': authors,
                    'genres': genres,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Daycomics.search_by_keyword('', False)