from bs4 import BeautifulSoup
from utils.Bases import Manga, Req

class Manga18fx(Manga, Req):
    def get_chapters(manga):
        response = Manga18fx.send_request(f'https://manga18fx.com/manga/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'a-h'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manga18fx.send_request(f'https://manga18fx.com/manga/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'read-content'}).find_all('img')
        images = [image['src'].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        template = f'https://manga18fx.com/search?q={keyword}&page=P_P_P_P' if keyword else f'https://manga18fx.com/page/P_P_P_P'
        page = 1
        prev_page = []
        while True:
            try:
                response = Manga18fx.send_request(template.replace('P_P_P_P', str(page)))
                soup = BeautifulSoup(response.text, 'html.parser')
                mangas = soup.find_all('div', {'class': 'bigor-manga'})
                results = {}
                if mangas == prev_page:
                    yield {}
                for manga in mangas:
                    contents = manga.find_all('a')
                    ti = contents[0]['title']
                    if absolute and keyword.lower() not in ti.lower():
                        continue
                    link = contents[0]['href'].split('/')[-1]
                    latest_chapter = contents[1]['href'].split('/')[-1]
                    results[ti] = {
                        'domain': 'bibimanga.com',
                        'url': link,
                        'latest_chapter': latest_chapter,
                    }
                prev_page = mangas
                yield results
                page += 1
            except HTTPError:
                yield {}
            except Timeout as error:
                raise error
            except RequestException:
                waiter()

    def get_db():
        return Manga18fx.search_by_keyword('', False)