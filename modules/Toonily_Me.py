from bs4 import BeautifulSoup
from utils.models import Manga

class Toonily_Me(Manga):
    domain = 'toonily.me'
    logo = 'https://toonily.me/static/sites/toonily/icons/favicon.ico'
    download_images_headers = {'Referer': 'https://toonily.me/'}

    def get_info(manga, wait=True):
        from contextlib import suppress
        response = Toonily_Me.send_request(f'https://toonily.me/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, rating, status, authors, chapters, genres, last_update = 10 * ['']
        info_box = soup.find('div', {'class': 'book-info'})
        with suppress(Exception): cover = f'https:{info_box.find("img")["data-src"]}'
        with suppress(Exception): title = info_box.find('div', {'class': 'name box'}).find('h1').get_text(strip=True)
        with suppress(Exception): alternative = info_box.find('div', {'class': 'name box'}).find('h2').get_text(strip=True)
        with suppress(Exception): summary = soup.find('div', {'class': 'section box mt-1 summary'}).find('p').get_text(strip=True)
        with suppress(Exception): rating = float(soup.find('span', {'class': 'score'}).contents[-1].strip())
        with suppress(Exception): status = info_box.find('div', {'class': 'post-status'}).find_all('div', {'class': 'summary-content'})[1].get_text(strip=True)
        for box in soup.find('div', {'class': 'meta box mt-1 p-10'}).find_all('p'):
            if 'Author' in box.get_text(strip=True):
                authors = [a.get_text(strip=True) for a in box.find_all('a')]
            elif 'Status' in box.get_text(strip=True):
                status = box.find('a').get_text(strip=True)
            elif 'Chapters' in box.get_text(strip=True):
                chapters = box.find('span').get_text(strip=True)
            elif 'Genre' in box.get_text(strip=True):
                genres = [a.get_text(strip=True) for a in box.find_all('a')]
            elif 'Last update' in box.get_text(strip=True):
                last_update = box.find('span').get_text(strip=True)
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Rating': rating,
            'Status': status,
            'Extras': {
                'Authors': authors,
                'Chapters': chapters,
                'Genres': genres,
                'Last update': last_update
            }
        }

    def get_chapters(manga, wait=True):
        response = Toonily_Me.send_request(f'https://toonily.me/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('ul', {'class': 'chapter-list'}).find_all('li')
        chapters_urls = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Toonily_Me.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Toonily_Me.send_request(f'https://toonily.me/{manga}/{chapter["url"]}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id': 'chapter-images'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        template = f'https://toonily.me/search?q={keyword}&page=P_P_P_P' if keyword else f'https://toonily.me/az-list?page=P_P_P_P'
        page = 1
        while True:
            response = Toonily_Me.send_request(template.replace('P_P_P_P', str(page)), wait=wait)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'book-item'})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'title'}).find('a')
                if absolute and keyword.lower() not in ti['title'].lower():
                    continue
                latest_chapter, genres, summary = '', '', ''
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'latest-chapter'})['title']
                with suppress(Exception): genres = manga.find('div', {'class': 'genres'}).get_text(strip=True, separator=', ')
                with suppress(Exception): summary = manga.find('div', {'class': 'summary'}).get_text(strip=True)
                results[ti['title']] = {
                    'domain': Toonily_Me.domain,
                    'url': ti['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'thumbnail': f'https:{manga.find("img")["data-src"]}',
                    'genres': genres,
                    'summary': summary,
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Toonily_Me.search_by_keyword('', False, wait=wait)