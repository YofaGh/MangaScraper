from bs4 import BeautifulSoup
from utils.models import Doujin

class Pururin(Doujin):
    domain = 'pururin.to'
    logo = 'https://pururin.to/assets/images/logo.png'

    def get_info(code):
        from contextlib import suppress
        response, _ = Pururin.send_request(f'https://pururin.to/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, pages, rating = 5 * ['']
        extras = {}
        with suppress(Exception):
            cover = soup.find('img', {'class': 'cover'})['src']
        with suppress(Exception):
            title = soup.find('h1').get_text(strip=True)
        with suppress(Exception):
            alternative = soup.find('h2').get_text(strip=True)
        with suppress(Exception):
            pages = soup.find('span', {'itemprop': 'numberOfPages'}).get_text(strip=True)
        with suppress(Exception):
            rating = float(soup.find('span', {'itemprop': 'ratingValue'}).get('content'))
        tag_box = soup.find('table', {'class': 'table table-info'}).find_all('tr')
        for box in tag_box:
            if 'Pages' in box.text or 'Ratings' in box.text:
                continue
            if 'Ranking' in box.text:
                with suppress(Exception):
                    extras['Ranking'] = box.find_all('td')[-1].get_text(strip=True)
            else:
                with suppress(Exception):
                    extras[box.find('td').get_text(strip=True)] = [a.get_text(strip=True) for a in box.find_all('a')]
        return {
            'Cover': cover,
            'Title': title,
            'Pages': pages,
            'Alternative': alternative,
            'Rating': rating,
            'Extras': extras,
        }

    def get_title(code):
        response, _ = Pururin.send_request(f'https://pururin.to/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True)
        return title

    def get_images(code):
        response, _ = Pururin.send_request(f'https://pururin.to/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'gallery-preview'}).find_all('img')
        images = [image['data-src'] if image.get('data-src') else image['src'] for image in images]
        images = [image.replace('t.', '.') for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        page = 1
        session = None
        while True:
            response, session = Pururin.send_request(f'https://pururin.to/search?q={keyword}&page={page}', session=session)
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('a', {'class': 'card card-gallery'})
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                if absolute and keyword.lower() not in doujin['title'].lower():
                    continue
                info = doujin.find('div', {'class': 'info'}).get_text(strip=True).split(', ')
                results[doujin['title']] = {
                    'domain': Pururin.domain,
                    'code': doujin['href'].split('/')[-1],
                    'thumbnail': doujin.find('img')['src'],
                    'author': info[0].split(' by ')[-1] ,
                    'language': info[1],
                    'total_pages': info[2].split()[0],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Pururin.search_by_keyword('', False)