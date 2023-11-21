from bs4 import BeautifulSoup
from utils.models import Manga

class Mangaforfree(Manga):
    domain = 'mangaforfree.net'
    logo = 'https://mangaforfree.net/wp-content/uploads/2023/02/cropped-Favicol-mangaNet-192x192.png'

    def get_info(manga, wait=True):
        from contextlib import suppress
        response = Mangaforfree.send_request(f'https://mangaforfree.net/manga/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, rating, status = 6 * ['']
        extras = {}
        info_box = soup.find('div', {'class': 'tab-summary'})
        with suppress(Exception): cover = info_box.find('img')['src']
        with suppress(Exception): title = soup.find('div', {'class': 'post-title'}).find('h1').contents[-1].strip()
        with suppress(Exception): summary = soup.find('div', {'class': 'summary__content'}).find('p').contents[-1].strip()
        with suppress(Exception): rating = float(info_box.find('div', {'class': 'post-total-rating'}).find('span').get_text(strip=True))
        with suppress(Exception): extras['Release'] = info_box.find('div', {'class': 'post-status'}).find_all('div', {'class': 'summary-content'})[0].get_text(strip=True)
        with suppress(Exception): status = info_box.find('div', {'class': 'post-status'}).find_all('div', {'class': 'summary-content'})[1].get_text(strip=True)
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

    def get_chapters(manga, wait=True):
        response = Mangaforfree.send_request(f'https://mangaforfree.net/manga/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        manga_id = soup.find('a', {'class': 'wp-manga-action-button'})['data-post']
        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = f'action=manga_get_chapters&manga={manga_id}'
        response = Mangaforfree.send_request('https://mangaforfree.net/wp-admin/admin-ajax.php', method='POST', headers=headers, data=data, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters_urls = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Mangaforfree.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Mangaforfree.send_request(f'https://mangaforfree.net/manga/{manga}/{chapter['url']}/', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Mangaforfree.send_request(f'https://mangaforfree.net/page/{page}?s={keyword}&post_type=wp-manga', wait=wait)
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
                    'domain': Mangaforfree.domain,
                    'url': link,
                    'latest_chapter': latest_chapter,
                    'thumbnail': manga.find('img')['src'],
                    'genres': genres,
                    'authors': authors,
                    'artists': artists,
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Mangaforfree.search_by_keyword('', False, wait=wait)

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
            return f'Chapter {new_name.split('.', 1)[0].zfill(3)}.{new_name.split('.', 1)[1]}{tail}'