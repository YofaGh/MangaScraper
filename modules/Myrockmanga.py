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

    def get_chapters(manga):
        response = Myrockmanga.send_request(f'https://myrockmanga.com/manga-detail/{manga}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('tr', {'class': 'chapter'})
        chapters_urls = [div.find('a')['href'].replace('/chapter/', '') for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Myrockmanga.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        response = Myrockmanga.send_request(f'https://myrockmanga.com/chapter/{chapter["url"]}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id': 'rendering'}).find_all('img')
        images = [image['src'] for image in images if image.has_attr('page')]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        while True:
            try:
                response = Myrockmanga.send_request(f'https://myrockmanga.com/Home/Search?search={keyword}', headers=Myrockmanga.headers, verify=False)
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
                with suppress(Exception): type = header.find_all('a')[1].get_text(strip=True)
                with suppress(Exception): lang = header.find('img', {'class': 'flag'})['src'].split('/')[-1].split('.')[0]
                with suppress(Exception): latest_chapter = manga.find('div', {'class': 'mdl-card__actions mdl-card--border'}).find('a')['href']
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
        while True:
            response = Myrockmanga.send_request(f'https://myrockmanga.com/Manga/Newest', method='POST', headers=Myrockmanga.get_db_headers, data=data.replace('P_P_P_P', str(page)), verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'col-xs-12 picture-card mdl-card shadow-z-1'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                header = manga.find('div', {'class': 'mdl-card__supporting-text mdl-color-text--grey-600'})
                ti = header.find('h4').find('a')
                type, lang, latest_chapter = '', '', ''
                with suppress(Exception): type = header.find_all('a')[1].get_text(strip=True)
                with suppress(Exception): lang = header.find('img', {'class': 'flag'})['src'].split('/')[-1].split('.')[0]
                with suppress(Exception): latest_chapter = manga.find('div', {'class': 'mdl-card__actions mdl-card--border'}).find('a')['href']
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
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'