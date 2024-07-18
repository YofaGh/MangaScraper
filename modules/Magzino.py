from bs4 import BeautifulSoup
from utils.models import Manga

class Magzino(Manga):
    domain = 'magzino.top'
    logo = 'https://magzino.top/storage/2023/06/cropped-nafiicon-192x192.png'
    image_headers = {'cookie': '_lscache_vary=621c4b8eafb4287a9451c2bda1936d41'}

    def get_info(manga):
        from contextlib import suppress
        response, _ = Magzino.send_request(f'https://magzino.top/all-books/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, summary, rating, status = 5 * ['']
        info_box = soup.find_all('div', {'class': 'post-content_item'})
        extras = {}
        with suppress(Exception): cover = soup.find('div', {'class': 'summary_image'}).find('img')['data-src']
        with suppress(Exception): title = soup.find('h1').get_text(strip=True)
        with suppress(Exception): summary = soup.find('div', {'class': 'summary__content'}).find('p').get_text(strip=True)
        with suppress(Exception): rating = float(soup.find('span', {'class': 'score font-meta total_votes'}).get_text(strip=True))
        with suppress(Exception): status = info_box[-1].find('div', {'class': 'summary-content'}).get_text(strip=True)
        for div in info_box[3:-1]:
            head = div.find('div', {'class': 'summary-heading'}).get_text(strip=True)
            if not head:
                head = 'genres'
            if div.find('div', {'class': 'asar-type-summary'}):
                with suppress(Exception): extras[head] = [link.get_text(strip=True).strip() for link in div.find_all('span')]
            else:
                with suppress(Exception): extras[head] = [link.get_text(strip=True).strip() for link in div.find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Summary': summary,
            'Rating': rating,
            'Status': status,
            'Extras': extras
        }

    def get_chapters(manga):
        response, _ = Magzino.send_request(f'https://magzino.top/all-books/{manga}/ajax/chapters', method='POST')
        soup = BeautifulSoup(response.text, 'html.parser')
        aas = soup.find_all('div', {'class': 'chap-a-span'})
        chapters = [{
            'url': aa.find('a')['href'].replace(f'https://magzino.top/all-books/{manga}/', '').rstrip('/'),
            'name': Magzino.rename_chapter(aa.find('a')['href'].replace(f'https://magzino.top/all-books/{manga}/', ''))
        } for aa in aas[::-1]]
        return chapters

    def get_images(manga, chapter):
        response, _ = Magzino.send_request(f'https://magzino.top/all-books/{manga}/{chapter["url"]}/', headers=Magzino.image_headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('img', {'class': 'wp-manga-chapter-img'})
        images = [div['data-src'].strip() for div in divs]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        data = {
            'action': 'madara_load_more',
            'page': 0,
            'template': 'madara-core/content/content-search',
            'vars[s]': keyword,
            'vars[post_type]': 'wp-manga',
        } if keyword else {
            'action': 'madara_load_more',
            'page': 0,
            'template': 'madara-core/content/content-archive',
            'vars[orderby]': 'post_title',
            'vars[post_type]': 'wp-manga',
            'vars[order]': 'ASC'
        }
        session = None
        class_name = 'row c-tabs-item__content' if keyword else 'col-12 col-md-6 badge-pos-1'
        while True:
            response, session = Magzino.send_request(f'https://magzino.top/ajax-call', session=session, method='POST', data=data)
            if not response.text:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': class_name})
            results = {}
            for manga in mangas:
                ti = manga.find('h3').find('a')
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                thumbnail, author, translators, genres, release_year, status, latest_chapter = 7 * ['']
                with suppress(Exception): thumbnail = manga.find('img')['src']
                with suppress(Exception): author = manga.find('div', {'class': 'mg_author'}).find('a').get_text(strip=True)
                with suppress(Exception): translators = [a.get_text(strip=True) for a in manga.find('div', {'class': 'mg_artists'}).find_all('a')]
                with suppress(Exception): genres = [a.get_text(strip=True) for a in manga.find('div', {'class': 'mg_genres'}).find_all('a')]
                with suppress(Exception): release_year = manga.find('div', {'class': 'release-year'}).find('a').get_text(strip=True)
                with suppress(Exception): status = manga.find('div', {'class': 'mg_status'}).find('div', {'class': 'summary-content'}).get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/', 5)[-1]
                results[ti.get_text(strip=True)] = {
                    'domain': Magzino.domain,
                    'url': ti['href'].split('/')[-2],
                    'latest_chapter': latest_chapter.rstrip('/'),
                    'thumbnail': thumbnail,
                    'author': author,
                    'translators': translators,
                    'genres': genres,
                    'release-year': release_year,
                    'status': status,
                    'page': data['page'] + 1
                }
            yield results
            data['page'] += 1

    def get_db():
        return Magzino.search_by_keyword('', False)

    def rename_chapter(chapter):
        return ' '.join([ch.capitalize() for ch in chapter.strip('/').split('-')]).replace('/', '.')