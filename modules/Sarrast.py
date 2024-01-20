from bs4 import BeautifulSoup
from utils.models import Manga

class Sarrast(Manga):
    domain = 'sarrast.com'

    def get_info(manga, wait=True):
        from contextlib import suppress
        response = Sarrast.send_request(f'https://sarrast.com/series/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, summary, rating, status, chapters, posted_on, type = 8 * ['']
        info_boxes = soup.find('div', {'class': 'flex mt-4 w-full bg-black bg-opacity-70 py-4 rounded-2xl text-white'}).find_all('div', {'class': 'flex-1 text-center'})
        with suppress(Exception): cover = f'https://sarrast.com/{soup.find("div", {"class": "flex-1"}).find("img")["src"]}'
        with suppress(Exception): title = soup.find('h1', {'class': 'text-xl font-black mt-2'}).get_text(strip=True)
        with suppress(Exception): summary = soup.find('p', {'class': 'mt-4 mb-2 text-sm'}).get_text(strip=True)
        with suppress(Exception): rating = float(info_boxes[1].find('div').get_text(strip=True))
        with suppress(Exception): status = info_boxes[2].find('div').get_text(strip=True)
        with suppress(Exception): chapters = info_boxes[0].find('div').get_text(strip=True)
        with suppress(Exception): posted_on = soup.find('div', {'id': 'postCreated'}).get_text(strip=True)
        with suppress(Exception): type = soup.find('a', {'class': 'ml-2'}).get_text(strip=True)
        return {
            'Cover': cover,
            'Title': title,
            'Summary': summary,
            'Rating': rating,
            'Status': status,
            'Extras': {
                'قسمت': chapters,
                'تاریخ انتشار': posted_on,
                'کتگوری': type
            },
        }

    def get_chapters(manga, wait=True):
        response = Sarrast.send_request(f'https://sarrast.com/series/{manga}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find('div', {'class': 'text-white mb-20 mt-8 relative px-4'}).find_all('a')
        chapters_urls = [div['href'].split('/')[-1] for div in divs[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Sarrast.rename_chapter(chapter_url.rsplit('-', 1)[0])
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        response = Sarrast.send_request(f'https://sarrast.com/series/{manga}/{chapter["url"]}/api', wait=wait).json()
        images = [f'https://sarrast.com{image["path"]}' for image in response['files']]
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        from requests.exceptions import HTTPError
        try:
            response = Sarrast.send_request(f'https://sarrast.com/search?value={keyword}', wait=wait)
            mangas = response.json()
            results = {}
            if not mangas:
                yield results
            for manga in mangas:
                results[manga['title']] = {
                    'domain': Sarrast.domain,
                    'url': manga['slug'],
                    'page': 1,
                    'thumbnail': ''
                }
            yield results
        except HTTPError:
            yield {}
        yield {}

    def get_db(wait=True):
        return Sarrast.search_by_keyword('', False, wait=wait)