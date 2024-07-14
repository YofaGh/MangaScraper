from bs4 import BeautifulSoup
from utils.models import Manga
from user_agents import LEECH

class Manga18(Manga):
    domain = 'manga18.club'
    logo = 'https://manga18.club/fav.png?v=1'
    headers = {'User-Agent': LEECH}

    def get_info(manga):
        from contextlib import suppress
        response = Manga18.send_request(f'https://manga18.club/manhwa/{manga}', headers=Manga18.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, summary, rating, status, authors, artists, views, categories = 10 * ['']
        info_box = soup.find('div', {'class': 'detail_story'})
        item_box = soup.find('div', {'class': 'detail_listInfo'})
        with suppress(Exception): cover = info_box.find('img')['src']
        with suppress(Exception): title = info_box.find('h1').get_text(strip=True)
        with suppress(Exception): summary = soup.find('div', {'class': 'detail_reviewContent'}).get_text(strip=True)
        with suppress(Exception): rating = float(info_box.find('div', {'class': 'detail_rate'}).find('span').get_text(strip=True).replace('/5', ''))
        with suppress(Exception): alternative = item_box.find(lambda tag: 'Other name' in tag.text).find('span').get_text(strip=True)
        with suppress(Exception): status = item_box.find(lambda tag: 'Status' in tag.text).find('span').get_text(strip=True)
        with suppress(Exception): authors = [a.get_text(strip=True) for a in item_box.find(lambda tag: 'Author' in tag.text).find_all('a')]
        with suppress(Exception): artists = [a.get_text(strip=True) for a in item_box.find(lambda tag: 'Artist' in tag.text).find_all('a')]
        with suppress(Exception): views = item_box.find(lambda tag: 'Views' in tag.text).find('span').get_text(strip=True)
        with suppress(Exception): categories = [a.get_text(strip=True) for a in item_box.find(lambda tag: 'Categories' in tag.text).find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Alternative': alternative,
            'Summary': summary,
            'Rating': rating,
            'Status': status,
            'Extras': {
                'Authors': authors,
                'Artists': artists,
                'Views': views,
                'Categories': categories
            }
        }

    def get_chapters(manga):
        response = Manga18.send_request(f'https://manga18.club/manhwa/{manga}', headers=Manga18.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find('div', {'class': 'chapter_box'}).find_all('li')
        chapters_urls = [li.find('a')['href'].split('/')[-1] for li in lis[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Manga18.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        import base64
        response = Manga18.send_request(f'https://manga18.club/manhwa/{manga}/{chapter["url"]}', headers=Manga18.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag:tag.name == 'script' and 'slides_p_path' in tag.text)
        images = script.text.split('[', 1)[1].split(']', 1)[0][:-1]
        images = [image.replace('"', '') for image in images.split(',')]
        images = [base64.b64decode(image).decode('utf-8') for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        while True:
            response = Manga18.send_request(f'https://manga18.club/list-manga/{page}?search={keyword}', headers=Manga18.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'col-md-3 col-sm-4 col-xs-6'})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('div', {'class': 'mg_name'}).find('a')
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                latest_chapter = ''
                with suppress(Exception): latest_chapter = manga.find('div', {'class': 'mg_chapter'}).find('a')['href'].split('/')[-1]
                results[ti.get_text(strip=True)] = {
                    'domain': Manga18.domain,
                    'url': ti['href'].split('/')[-1],
                    'thumbnail': manga.find('img')['src'],
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Manga18.search_by_keyword('', False)