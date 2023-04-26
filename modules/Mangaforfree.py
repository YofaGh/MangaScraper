from bs4 import BeautifulSoup
from utils.models import Manga

class Mangaforfree(Manga):
    domain = 'mangaforfree.net'

    def get_chapters(manga):
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as ec
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://mangaforfree.net/manga/{manga}')
        WebDriverWait(browser, 60).until(ec.presence_of_element_located((By.XPATH, '//li[@class="wp-manga-chapter  "]')))
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Mangaforfree.send_request(f'https://mangaforfree.net/manga/{manga}/{chapter}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Mangaforfree.send_request(f'https://mangaforfree.net/page/{page}?s={keyword}&post_type=wp-manga')
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
                        head = content.find('h5').contents[0].replace('\n', '').replace(' ', '').replace('\t', '')
                        if head == 'Authors':
                            authors = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Artists':
                            artists = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Genres':
                            genres = ', '.join([a.contents[0] for a in content.find_all('a')])
                        if head == 'Status':
                            status = content.find('div', {'class': 'summary-content'}).contents[0].replace('\n', '').replace(' ', '').replace('\t', '')
                with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                results[ti] = {
                    'domain': Mangaforfree.domain,
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
        return Mangaforfree.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        tail = ' Raw' if 'raw' in chapter else ''
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
            return f'Chapter {int(new_name):03d}{tail}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}{tail}'