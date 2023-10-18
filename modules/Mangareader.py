from bs4 import BeautifulSoup
from utils.models import Manga

class Mangareader(Manga):
    domain = 'mangareader.mobi'
    logo = 'https://mangareader.mobi/frontend/imgs/favicon16.png'

    def get_chapters(manga):
        response = Mangareader.send_request(f'https://mangareader.mobi/manga/{manga}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('div', {'class':'cl'}).find_all('a')
        chapters = [div['href'].split('/')[-1] for div in divs[::-1]]
        chapters_urls = [chapter.replace(f'{manga}-','') for chapter in chapters]
        chapters = [{
            'url': chapter_url,
            'name': Mangareader.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        chapter_url = chapter['url']
        if f'{manga}-' in chapter_url:
            chapter_url = chapter_url.replace(f'{manga}-','')
        response = Mangareader.send_request(f'https://mangareader.mobi/chapter/{manga}-{chapter_url}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id':'readerarea'}).find('p').text
        images = images.split(',')
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        from contextlib import suppress
        page = 1
        while True:
            try:
                response = Mangareader.send_request(f'https://mangareader.mobi/search?s={keyword}&page={page}', verify=False)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find('div', {'id': 'content'}).find('ul').find_all('li')
            if len(mangas) == 0:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'left'}).find('a')
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                latest_chapter, genres, status = '', '', ''
                contents = manga.find('div', {'class': 'info'}).findChildren('span', recursive=False)
                for content in contents:
                    if content.has_attr('class'):
                        genres = content.get_text(strip=True)
                    elif content.find('b'):
                        status = content.get_text().replace('Status: ', '').strip()
                    else:
                        with suppress(Exception): latest_chapter = content.find('a')['href'].split('/')[-1]
                results[ti.get_text(strip=True)] = {
                    'domain': Mangareader.domain,
                    'url': ti['href'].split('/')[-1],
                    'latest_chapter': latest_chapter,
                    'thumbnail': manga.find('img')['src'],
                    'genres': genres,
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Mangareader.search_by_keyword('', False)