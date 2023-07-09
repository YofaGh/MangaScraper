from bs4 import BeautifulSoup
from utils.models import Manga

class Bato(Manga):
    domain = 'bato.to'

    def get_chapters(manga):
        response = Bato.send_request(f'https://bato.to/title/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('div', {'class': 'group flex flex-col-reverse'}).find_all('a', {'class': 'link-hover link-primary visited:text-accent'})
        chapters = [link['href'].split('/')[-1] for link in links]
        return chapters

    def get_images(manga, chapter):
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://bato.to/chapter/{chapter.split("-")[0]}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        images = soup.find('div', {'class': 'd-flex flex-column align-items-center align-content-center'}).find_all('img')
        images = [image['src'].strip() for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Bato.send_request(f'https://bato.to/v3x-search?word={keyword}&page={page}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'flex border-b border-b-base-200 pb-5'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for index, manga in enumerate(mangas):
                ti = manga.find('h3').find('a')
                if absolute and keyword.lower() not in ti.text.lower():
                    continue
                alias, genres, latest_chapter = '', '', ''
                with suppress(Exception): alias = manga.find('div', {'data-hk': f'0-0-3-{index}-4-0'}).text
                with suppress(Exception): genres = manga.find('div', {'data-hk': f'0-0-3-{index}-6-0'}).text
                with suppress(Exception): latest_chapter = manga.find('div', {'data-hk': f'0-0-3-{index}-7-1-0-0'}).find('a')['href'].split('/')[-1]
                results[ti.text] = {
                    'domain': Bato.domain,
                    'url': ti['href'].replace('/title/', ''),
                    'latest_chapter': latest_chapter,
                    'genres': genres,
                    'alias': alias,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Bato.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        chap = chapter.split('-', 1)[1] if '-' in chapter else chapter
        new_name = ''
        reached_number = False
        for ch in chap:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chap
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'