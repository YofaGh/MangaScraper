from bs4 import BeautifulSoup
from utils.models import Doujin
from user_agents import MOZILLA

class Hentairead(Doujin):
    domain = 'hentairead.com'
    logo = 'https://i0.wp.com/hentairead.com/wp-content/uploads/2022/01/cropped-favicon.png'
    headers = {'User-Agent': MOZILLA}
    is_coded = False

    def get_info(code):
        from contextlib import suppress
        from datetime import datetime
        response, _ = Hentairead.send_request(f'https://hentairead.com/hentai/{code}/', headers=Hentairead.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, pages, uploaded, rating = 6 * ['']
        extras = {}
        with suppress(Exception): cover = soup.find('div', {'class': 'c-image-hover'}).find('img')['data-src'].rsplit('?', 1)[0]
        with suppress(Exception): title = soup.find('h1').get_text(strip=True)
        with suppress(Exception): alternative = soup.find('h2').get_text(strip=True)
        with suppress(Exception): rating = float(soup.find('span', {'class': 'score font-meta total_votes'}).get_text(strip=True).split(' ')[0])
        tag_box = soup.find('div', {'class': 'post-summary'}).find_all('div', {'class': 'post-meta'})
        for box in tag_box:
            if 'Pages' in box.text:
                with suppress(Exception): pages = box.find('div', {'class': 'tag-name'}).get_text(strip=True)
            elif 'Uploaded' in box.text:
                with suppress(Exception): uploaded = box.find('span', {'class': 'post-meta-value'}).get_text(strip=True)
            elif 'Views' in box.text:
                with suppress(Exception): extras['Views'] = box.find('div', {'class': 'tag-name'}).get_text(strip=True)
            else:
                with suppress(Exception): 
                    extras[box.find('span').contents[0].strip()] = [tag.get_text(strip=True) for tag in box.find_all('span', {'class': 'tag-name'})]
        return {
            'Cover': cover,
            'Title': title,
            'Pages': pages,
            'Alternative': alternative,
            'Rating': rating,
            'Extras': extras,
            'Dates': {
                'Uploaded': datetime.strptime(uploaded, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    def get_title(code):
        response, _ = Hentairead.send_request(f'https://hentairead.com/hentai/{code}/', headers=Hentairead.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True)
        return title

    def get_images(code):
        response, _ = Hentairead.send_request(f'https://hentairead.com/hentai/{code}/', headers=Hentairead.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('ul', {'class': 'chapter-images-list lazy-listing__list'}).find_all('img')
        images = [image['data-src'].split('?', 1)[0] for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        session = None
        template = f'https://hentairead.com/page/P_P_P_P/?s={keyword}'
        if not keyword:
            template = f'https://hentairead.com/hentai/page/P_P_P_P/?m_orderby=alphabet&m_order=desc'
        while True:
            try:
                response, session = Hentairead.send_request(template.replace('P_P_P_P', str(page)), session=session, headers=Hentairead.headers)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'grid-item badge-pos-1'})
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                ti = doujin.find('h3').find('a')
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                alternative, parody, artist, views, rating, total_pages, tags = '', '', '', '', '', '', []
                with suppress(Exception): alternative = doujin.find('div', {'class': 'item-alter-title'}).get_text(strip=True)
                with suppress(Exception): parody = doujin.find('div', {'class': 'item-parody'}).get_text(strip=True)
                with suppress(Exception): artist = doujin.find('div', {'class': 'item-by-artist'}).get_text(strip=True)
                with suppress(Exception): tags = [tag.get_text(strip=True) for tag in doujin.find_all('span', {'class': 'tag-name'})]
                with suppress(Exception): views = doujin.find('div', {'class': 'item__total-views'}).get_text(strip=True)
                with suppress(Exception): rating = float(doujin.find('div', {'class': 'item__rating'}).get_text(strip=True))
                with suppress(Exception): total_pages = int(doujin.find('div', {'class': 'item__total-pages'}).get_text(strip=True))
                results[ti.get_text(strip=True)] = {
                    'domain': Hentairead.domain,
                    'code': ti['href'].split('/')[-2],
                    'thumbnail': doujin.find('img')['data-src'].split('?', 1)[0],
                    'alternative': alternative,
                    'parody': parody,
                    'artist': artist,
                    'tags': tags,
                    'views': views,
                    'rating': rating,
                    'total_pages': total_pages,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Hentairead.search_by_keyword('', False)