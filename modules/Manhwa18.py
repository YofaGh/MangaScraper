from bs4 import BeautifulSoup
from utils.models import Manga

class Manhwa18(Manga):
    domain = 'manhwa18.com'
    logo = 'https://manhwa18.com/favicon1.ico'

    def get_info(manga, wait=True):
        from contextlib import suppress
        response = Manhwa18.send_request(f'https://manhwa18.com/manga/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, rating, status, latest_reading, views = 8 * ['']
        info_box = soup.find('main', {'class': 'section-body'})
        extras = {}
        with suppress(Exception): cover = soup.find('meta', {'property': 'og:image'})['content']
        with suppress(Exception): title = info_box.find('span', {'class': 'series-name'}).get_text(strip=True)
        with suppress(Exception): summary = info_box.find('div', {'class': 'summary-content'}).get_text(strip=True)
        with suppress(Exception): 
            rating = float(info_box.find_all('div', {'class': 'col-4 statistic-item'})[0].find('div', {'class': 'statistic-value'}).get_text(strip=True).replace('/5', ''))
        with suppress(Exception): views = info_box.find_all('div', {'class': 'col-4 statistic-item'})[1].find('div', {'class': 'statistic-value'}).get_text(strip=True)
        with suppress(Exception): latest_reading = info_box.find('time')['datetime']
        for box in info_box.find('div', {'class': 'series-information'}).find_all('div', {'class': 'info-item'}):
            if 'Other name' in box.text:
                alternative = box.find('span', {'class': 'info-value'}).get_text(strip=True)
            elif 'Status' in box.text:
                status = box.find('a').get_text(strip=True)
            else:
                extras[box.find('span').get_text(strip=True).replace(':', '')] = [a.get_text(strip=True) for a in box.find_all('a')]
        extras['Views'] = views
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Rating': rating,
            'Status': status,
            'Extras': extras,
            'Dates': {
                'Latest reading': latest_reading,
            },
        }

    def get_chapters(manga, wait=True):
        response = Manhwa18.send_request(f'https://manhwa18.com/manga/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        aas = soup.find('ul', {'class':'list-chapters at-series'}).find_all('a')
        chapters_urls = [aa['href'].split('/')[-1] for aa in aas[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Manhwa18.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Manhwa18.send_request(f'https://manhwa18.com/manga/{manga}/{chapter["url"]}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id':'chapter-content'}).find_all('img')
        images = [image['data-src'] for image in images]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Manhwa18.send_request(f'https://manhwa18.com/tim-kiem?q={keyword}&page={page}', wait=wait)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'thumb-item-flow col-6 col-md-2'})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'thumb_attr series-title'}).find('a')['title']
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    'domain': Manhwa18.domain,
                    'url': manga.find('a')['href'].split('/')[-1],
                    'latest_chapter': manga.find('div', {'class': 'thumb-detail'}).find('a')['href'].split('/')[-1],
                    'thumbnail': manga.find('div', {'class': 'a6-ratio'}).find('div')['data-bg'],
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Manhwa18.search_by_keyword('', False, wait=wait)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        new_name = new_name.rsplit('.', 1)[0]
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'