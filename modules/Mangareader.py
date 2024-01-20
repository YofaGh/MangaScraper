from bs4 import BeautifulSoup
from utils.models import Manga

class Mangareader(Manga):
    domain = 'mangareader.mobi'
    logo = 'https://mangareader.mobi/frontend/imgs/favicon16.png'

    def get_info(manga, wait=True):
        from contextlib import suppress
        response = Mangareader.send_request(f'https://mangareader.mobi/manga/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, status, authors, views, genres = 8 * ['']
        info_box = soup.find('div', {'class': 'imgdesc'})
        with suppress(Exception): cover = info_box.find('img')['src']
        with suppress(Exception): title = soup.find('div', {'class': 'rm'}).find('h1').get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find(lambda tag: tag.name == 'li' and 'Alternative' in tag.text).contents[1][1:].strip()
        with suppress(Exception): summary = soup.find('div', {'id': 'noidungm'}).get_text(strip=True)
        with suppress(Exception): status = info_box.find_all(lambda tag: tag.name == 'li' and 'Status' in tag.text)[2].get_text(strip=True).replace('Status:', '').strip()
        with suppress(Exception): authors = info_box.find_all(lambda tag: tag.name == 'li' and 'Author' in tag.text)[2].get_text(strip=True).replace('Author:', '')
        with suppress(Exception): views = info_box.find_all(lambda tag: tag.name == 'li' and 'Views' in tag.text)[2].get_text(strip=True).replace('Views:', '').replace('Views:', '')
        with suppress(Exception): genres = [a.get_text(strip=True) for a in info_box.find_all(lambda tag: tag.name == 'li' and 'Genres' in tag.text)[2].find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Status': status,
            'Extras': {
                'Authors': authors,
                'Views': views,
                'Genres': genres
            }
        }

    def get_chapters(manga, wait=True):
        response = Mangareader.send_request(f'https://mangareader.mobi/manga/{manga}', verify=False, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('div', {'class':'cl'}).find_all('a')
        chapters = [div['href'].split('/')[-1] for div in divs[::-1]]
        chapters_urls = [chapter.replace(f'{manga}-','') for chapter in chapters]
        chapters = [{
            'url': chapter_url,
            'name': Mangareader.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        chapter_url = chapter['url']
        if f'{manga}-' in chapter_url:
            chapter_url = chapter_url.replace(f'{manga}-','')
        response = Mangareader.send_request(f'https://mangareader.mobi/chapter/{manga}-{chapter_url}', verify=False, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'id':'readerarea'}).find('p').get_text(strip=True).split(',')
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        from contextlib import suppress
        page = 1
        while True:
            try:
                response = Mangareader.send_request(f'https://mangareader.mobi/search?s={keyword}&page={page}', verify=False, wait=wait)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find('div', {'id': 'content'}).find('ul').find_all('li')
            if not mangas:
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

    def get_db(wait=True):
        return Mangareader.search_by_keyword('', False, wait=wait)