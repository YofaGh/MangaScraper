from bs4 import BeautifulSoup
from utils.models import Manga

class Myrockmanga(Manga):
    domain = 'myrockmanga.com'
    logo = 'https://myrockmanga.com/Content/Img/logo_square.png'
    headers = {'cookie': 'culture=en'}
    get_db_headers = {'cookie': 'culture=en', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    langs = {
        'us': 'English',
        'vn': 'Vietnamese',
        'it': 'Italian',
        'fr': 'French',
        'es': 'Spanish'
    }

    def get_info(manga):
        from contextlib import suppress
        response, _ = Myrockmanga.send_request(f'https://myrockmanga.com/manga-detail/{manga}', headers=Myrockmanga.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, rating, status, genres = 7 * ['']
        extras = {}
        with suppress(Exception):
            cover = soup.find('div', {'class': 'manga-top-img'}).find('img')['src']
        with suppress(Exception):
            title = soup.find('h1', {'class': 'title text-lg-left'}).get_text(strip=True)
        with suppress(Exception):

            alternative = soup.find('table').find(lambda tag: tag.name == 'tr' and not tag.find('th') and tag.find('td')).find('td').get_text(strip=True)
        with suppress(Exception):
            summary = soup.find('div', {'class': 'summary'}).find('p').get_text(strip=True)
        with suppress(Exception):
            rating = float(soup.find('div', {'class': 'rating'}).find('span').get_text(strip=True).replace('/ 10', ''))/2
        with suppress(Exception):
            genres = [a.get_text(strip=True) for a in soup.find('div', {'class': 'genres'}).find_all('a')]
        for box in soup.find('table').find_all(lambda tag: tag.name == 'tr' and tag.find('th') and tag.find('td')):
            if 'Status' in box.text:
                status = box.find('td').get_text(strip=True)
            else:
                extras[box.find('th').get_text(strip=True)] = [a.get_text(strip=True) for a in box.find_all('a')]
        extras['Genres'] = genres
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
        response, _ = Myrockmanga.send_request(f'https://myrockmanga.com/manga-detail/{manga}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('tr', {'class': 'chapter'})
        chapters_urls = [div.find('a')['href'].replace('/chapter/', '') for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Myrockmanga.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response, _ = Myrockmanga.send_request(f'https://myrockmanga.com/chapter/{chapter["url"]}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id': 'rendering'}).find_all('img')
        images = [image['src'] for image in images if image.has_attr('page')]
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        session = None
        while True:
            try:
                response, session = Myrockmanga.send_request(f'https://myrockmanga.com/Home/Search?search={keyword}', session=session, headers=Myrockmanga.headers, verify=False)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            sections = soup.find_all('div', {'class': 'row'})
            mangas = []
            for section in sections:
                if section.find('div', {'class': 'collection shadow-z-1-home'}) and section.find('h4', {'class': 'group-header'}).get_text(strip=True) == 'Manga':
                    mangas = section.find_all('div', {'class': 'col-xs-12 picture-card mdl-card shadow-z-1'})
                    break
            results = {}
            for manga in mangas:
                header = manga.find('div', {'class': 'mdl-card__supporting-text mdl-color-text--grey-600'})
                ti = header.find('h4').find('a')
                if absolute and keyword.lower() not in ti['title'].lower():
                    continue
                type, lang, latest_chapter = '', '', ''
                with suppress(Exception):
                    type = header.find_all('a')[1].get_text(strip=True)
                with suppress(Exception):
                    lang = header.find('img', {'class': 'flag'})['src'].split('/')[-1].split('.')[0]
                with suppress(Exception):
                    latest_chapter = manga.find('div', {'class': 'mdl-card__actions mdl-card--border'}).find('a')['href']
                results[ti['title']] = {
                    'domain': Myrockmanga.domain,
                    'url': ti['href'].replace('/manga-detail/', ''),
                    'type': type,
                    'lang': Myrockmanga.langs[lang],
                    'latest_chapter': latest_chapter.replace('/chapter/', ''),
                    'thumbnail': manga.find('img')['src'],
                    'page': 1
                }
            yield results
            yield {}

    def get_db():
        from contextlib import suppress
        page = 1
        data = 'Type=1&Page=P_P_P_P&Lang=all&Dir=NewPostedDate&filterCategory=All'
        session = None
        while True:
            response, session = Myrockmanga.send_request('https://myrockmanga.com/Manga/Newest', session=session, method='POST', headers=Myrockmanga.get_db_headers, data=data.replace('P_P_P_P', str(page)), verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'col-xs-12 picture-card mdl-card shadow-z-1'})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                header = manga.find('div', {'class': 'mdl-card__supporting-text mdl-color-text--grey-600'})
                ti = header.find('h4').find('a')
                type, lang, latest_chapter = '', '', ''
                with suppress(Exception):
                    type = header.find_all('a')[1].get_text(strip=True)
                with suppress(Exception):
                    lang = header.find('img', {'class': 'flag'})['src'].split('/')[-1].split('.')[0]
                with suppress(Exception):
                    latest_chapter = manga.find('div', {'class': 'mdl-card__actions mdl-card--border'}).find('a')['href']
                results[ti.get_text(strip=True)] = {
                    'domain': Myrockmanga.domain,
                    'url': ti['href'].replace('/manga-detail/', ''),
                    'type': type,
                    'lang': Myrockmanga.langs[lang],
                    'latest_chapter': latest_chapter.replace('/chapter/', ''),
                    'page': page
                }
            yield results
            page += 1

    def rename_chapter(chapter):
        chapter = chapter.split('/')[-1]
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
        new_name = new_name.rstrip('.')
        try:
            return f'Chapter {int(new_name):03d}'
        except ValueError:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'