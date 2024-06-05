from bs4 import BeautifulSoup
from utils.models import Manga

class Bibimanga(Manga):
    domain = 'bibimanga.com'
    logo = 'https://bibimanga.com/wp-content/uploads/2021/06/FAV-300x300.png'

    def get_info(manga):
        from contextlib import suppress
        response = Bibimanga.send_request(f'https://bibimanga.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, rating, status = 6 * ['']
        extras = {}
        info_box = soup.find('div', {'class': 'tab-summary'})
        with suppress(Exception): cover = info_box.find('img')['data-src']
        with suppress(Exception): title = soup.find('div', {'class': 'post-title'}).find('h1').get_text(strip=True)
        with suppress(Exception): summary = soup.find('div', {'class': 'summary__content'}).get_text(strip=True)
        with suppress(Exception): rating = float(info_box.find('div', {'class': 'post-total-rating'}).find('span').get_text(strip=True))
        with suppress(Exception): status = info_box.find('div', {'class': 'post-status'}).find('div', {'class': 'summary-content'}).get_text(strip=True)
        for box in soup.find('div', {'class': 'post-content'}).find_all('div', {'class': 'post-content_item'}):
            if 'Rating' in box.get_text(strip=True):
                continue
            elif 'Alternative' in box.get_text(strip=True):
                with suppress(Exception): alternative = box.find('div', {'class': 'summary-content'}).get_text(strip=True)
            else:
                heading = box.find('div', {'class': 'summary-heading'}).get_text(strip=True).replace('(s)', '')
                info = box.find('div', {'class': 'summary-content'})
                if info.find('a'):
                    extras[heading] = [a.get_text(strip=True) for a in info.find_all('a')]
                else:
                    extras[heading] = box.find('div', {'class': 'summary-content'}).get_text(strip=True)
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Rating': rating,
            'Status': status,
            'Extras': extras
        }

    def get_chapters(manga):
        response = Bibimanga.send_request(f'https://bibimanga.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters_urls = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Bibimanga.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Bibimanga.send_request(f'https://bibimanga.com/manga/{manga}/{chapter["url"]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class':'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Bibimanga.send_request(f'https://bibimanga.com/page/{page}?s={keyword}&post_type=wp-manga')
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
                        if 'Authors' in content.text:
                            authors = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Artists' in content.text:
                            artists = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Genres' in content.text:
                            genres = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                        if 'Status' in content.text:
                            status = content.find('div', {'class': 'summary-content'}).get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[ti] = {
                    'domain': Bibimanga.domain,
                    'url': link,
                    'latest_chapter': latest_chapter,
                    'thumbnail': manga.find('img')['data-src'],
                    'genres': genres,
                    'authors': authors,
                    'artists': artists,
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Bibimanga.search_by_keyword('', False)