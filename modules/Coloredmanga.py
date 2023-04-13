from bs4 import BeautifulSoup
from utils.Bases import Manga, Req

class Coloredmanga(Manga, Req):
    def get_chapters(manga):
        response = Coloredmanga.send_request(f'https://coloredmanga.com/mangas/{manga}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters = [div.find('a')['href'].replace(f'https://coloredmanga.com/mangas/{manga}/', '')[:-1] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Coloredmanga.send_request(f'https://coloredmanga.com/mangas/{manga}/{chapter}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['src'].strip() for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from utils.assets import waiter
        from contextlib import suppress
        from requests.exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Coloredmanga.send_request(f'https://coloredmanga.com/page/{page}/?s={keyword}&post_type=wp-manga')
                soup = BeautifulSoup(response.text, 'html.parser')
                mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
                results = {}
                for manga in mangas:
                    tilink = manga.find('div', {'class', 'post-title'})
                    if absolute and keyword.lower() not in manga.find('a')['href']:
                        continue
                    latest_chapter, authors, artists, genres, status, release_date = '', '', '', '', '', ''
                    contents = manga.find_all('div', {'class': 'post-content_item'})
                    for content in contents:
                        with suppress(Exception):
                            head = content.find('h5').contents[0].replace('\n', '').replace(' ', '')
                            if head == 'Authors':
                                authors = ', '.join([a.contents[0] for a in content.find_all('a')])
                            if head == 'Artists':
                                artists = ', '.join([a.contents[0] for a in content.find_all('a')])
                            if head == 'Genres':
                                genres = ', '.join([a.contents[0] for a in content.find_all('a')])
                            if head == 'Status':
                                status = content.find('div', {'class': 'summary-content'}).contents[0].replace('\n', '').replace(' ', '')
                            if head == 'Release':
                                release_date = content.find('a').contents[0]
                    with suppress(Exception): latest_chapter = manga.find('span', {'class': 'font-meta chapter'}).find('a')['href'].split('/')[-2]
                    results[tilink.find('a').contents[0]] = {
                        'domain': 'coloredmanga.com',
                        'url': tilink.find('a')['href'].replace('https://coloredmanga.com/mangas/','')[:-1],
                        'latest_chapter': latest_chapter,
                        'genres': genres,
                        'authors': authors,
                        'artists': artists,
                        'status': status,
                        'release_date': release_date
                    }
                yield results
                page += 1
            except HTTPError:
                yield {}
            except Timeout as error:
                raise error
            except RequestException:
                waiter()

    def get_db():
        return Coloredmanga.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        beginner = 'Chapter'
        if 'volume' in chapter:
            beginner = 'Volume'
        elif 'number' in chapter:
            beginner = 'Number'
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-._' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'{beginner} {int(new_name):03d}'
        except:
            return f'{beginner} {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'