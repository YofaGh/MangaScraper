from bs4 import BeautifulSoup
from utils.models import Doujin

class Luscious(Doujin):
    domain = 'luscious.net'
    logo = 'https://www.luscious.net/assets/logo.png'

    def get_info(code, wait=True):
        from datetime import datetime
        from contextlib import suppress
        response = Luscious.send_request(f'https://www.luscious.net/albums/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, alternative, pages = 4 * ['']
        info_box = soup.find('div', {'class': 'album-info-wrapper'})
        extras, dates, tags = {}, {}, []
        with suppress(Exception): cover = soup.find('div', {'class': 'picture-card-outer'}).find('img')['src']
        with suppress(Exception): title = soup.find('h1', {'class': 'o-h1 album-heading'}).get_text(strip=True)
        with suppress(Exception): alternative = info_box.find('h2').get_text(strip=True)
        with suppress(Exception): extras['Language'] = info_box.find('a', {'class': 'language_flags-module__link--dp0Rr'}).get_text(strip=True)
        for box in info_box.find_all('span', {'class': 'album-info-item'}):
            if 'pictures' in box.text:
                with suppress(Exception): pages = box.get_text(strip=True).replace(' pictures', '')
            else:
                with suppress(Exception): dates[box.find('strong').get_text(strip=True)] = datetime.strptime(box.contents[-1], '%B %dth, %Y').strftime('%Y-%m-%d %H:%M:%S')
        for box in info_box.find_all('div', {'class': 'album-info-item'}):
            with suppress(Exception): extras[box.find('strong').get_text(strip=True)[:-1]] = [a.get_text(strip=True) for a in box.find_all('a')]
        for box in info_box.find_all('div', {'class': 'o-tag--category'}):
            with suppress(Exception): extras[box.find('strong').get_text(strip=True)[:-1]] = [a.get_text(strip=True) for a in box.find_all('a')]
        for box in info_box.find_all('div', {'class': 'o-tag--secondary'}):
            with suppress(Exception): tags.append(box.contents[0])
        extras['Album Description'] = soup.find('div', {'class': 'album-description'}).get_text(strip=True)
        extras['Tags'] = tags
        return {
            'Cover': cover,
            'Title': title,
            'Pages': pages,
            'Alternative': alternative,
            'Extras': extras,
            'Dates': dates
        }

    def get_title(code, wait=True):
        response = Luscious.send_request(f'https://www.luscious.net/albums/{code}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class', 'o-h1 album-heading'}).get_text(strip=True)
        return title

    def get_images(code, wait=True):
        data = 'https://apicdn.luscious.net/graphql/nobatch/?operationName=PictureListInsideAlbum&query=%2520query%2520PictureListInsideAlbum%28%2524input%253A%2520PictureListInput%21%29%2520%257B%2520picture%2520%257B%2520list%28input%253A%2520%2524input%29%2520%257B%2520info%2520%257B%2520...FacetCollectionInfo%2520%257D%2520items%2520%257B%2520url_to_original%2520position%2520%257B%2520category%2520text%2520url%2520%257D%2520thumbnails%2520%257B%2520width%2520height%2520size%2520url%2520%257D%2520%257D%2520%257D%2520%257D%2520%257D%2520fragment%2520FacetCollectionInfo%2520on%2520FacetCollectionInfo%2520%257B%2520page%2520total_pages%2520%257D%2520&variables=%7B%22input%22%3A%7B%22filters%22%3A%5B%7B%22name%22%3A%22album_id%22%2C%22value%22%3A%22__album__id__%22%7D%5D%2C%22display%22%3A%22position%22%2C%22items_per_page%22%3A50%2C%22page%22%3A__page__number__%7D%7D'
        response = Luscious.send_request(data.replace('__album__id__', str(code)).replace('__page__number__', '1'), wait=wait).json()
        total_pages = response['data']['picture']['list']['info']['total_pages']
        images = [item['url_to_original'] for item in response['data']['picture']['list']['items']]
        for page in range(2,total_pages + 1):
            response = Luscious.send_request(data.replace('__album__id__', str(code)).replace('__page__number__', str(page)), wait=wait).json()
            new_images = [item['url_to_original'] for item in response['data']['picture']['list']['items']]
            images.extend(new_images)
        return images, False

    def search_by_keyword(keyword, absolute, wait=True):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        data = 'https://apicdn.luscious.net/graphql/nobatch/?operationName=AlbumList&query=%2520query%2520AlbumList%28%2524input%253A%2520AlbumListInput%21%29%2520%257B%2520album%2520%257B%2520list%28input%253A%2520%2524input%29%2520%257B%2520info%2520%257B%2520...FacetCollectionInfo%2520%257D%2520items%2520%257B%2520...AlbumInSearchList%2520%257D%2520%257D%2520%257D%2520%257D%2520fragment%2520FacetCollectionInfo%2520on%2520FacetCollectionInfo%2520%257B%2520total_pages%2520%257D%2520fragment%2520AlbumInSearchList%2520on%2520Album%2520%257B%2520__typename%2520id%2520title%2520%257D%2520&variables=%7B%22input%22%3A%7B%22items_per_page%22%3A30%2C%22display%22%3A%22search_score%22%2C%22filters%22%3A%5B%7B%22name%22%3A%22album_type%22%2C%22value%22%3A%22manga%22%7D%2C%7B%22name%22%3A%22audience_ids%22%2C%22value%22%3A%22%2B1%2B3%2B5%22%7D%2C%7B%22name%22%3A%22language_ids%22%2C%22value%22%3A%22%2B1%2B100%2B101%2B2%2B3%2B4%2B5%2B6%2B8%2B9%2B99%22%7D%2C%7B%22name%22%3A%22search_query%22%2C%22value%22%3A%22__keyword__%22%7D%5D%2C%22page%22%3A__page__number__%7D%7D'
        total_pages = 1000
        page = 1
        while True:
            if page > total_pages:
                yield {}
            try:
                response = Luscious.send_request(data.replace('__keyword__', keyword).replace('__page__number__', str(page)), wait=wait).json()
                total_pages = response['data']['album']['list']['info']['total_pages']
            except HTTPError:
                yield {}
            doujins = response['data']['album']['list']['items']
            results = {}
            for doujin in doujins:
                name = doujin['title']
                code = doujin['id']
                tags, genres = '', ''
                with suppress(Exception): tags = ', '.join([tag['text'] for tag in doujin['tags']])
                with suppress(Exception): genres = ', '.join([tag['title'] for tag in doujin['genres']])
                if absolute and keyword.lower() not in name.lower():
                    continue
                results[name] = {
                    'domain': Luscious.domain,
                    'code': code,
                    'thumbnail': doujin['cover']['url'],
                    'genres': genres,
                    'tags': tags,
                    'page': page
                }
            yield results
            page += 1

    def get_db(wait=True):
        return Luscious.search_by_keyword('', False, wait=wait)