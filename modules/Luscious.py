from bs4 import BeautifulSoup
from utils.models import Doujin

class Luscious(Doujin):
    domain = 'luscious.net'
    logo = 'https://www.luscious.net/assets/logo.png'

    def get_title(code):
        response = Luscious.send_request(f'https://www.luscious.net/albums/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class', 'o-h1 album-heading'}).get_text(strip=True)
        return title

    def get_images(code):
        data = 'https://apicdn.luscious.net/graphql/nobatch/?operationName=PictureListInsideAlbum&query=%2520query%2520PictureListInsideAlbum%28%2524input%253A%2520PictureListInput%21%29%2520%257B%2520picture%2520%257B%2520list%28input%253A%2520%2524input%29%2520%257B%2520info%2520%257B%2520...FacetCollectionInfo%2520%257D%2520items%2520%257B%2520url_to_original%2520position%2520%257B%2520category%2520text%2520url%2520%257D%2520thumbnails%2520%257B%2520width%2520height%2520size%2520url%2520%257D%2520%257D%2520%257D%2520%257D%2520%257D%2520fragment%2520FacetCollectionInfo%2520on%2520FacetCollectionInfo%2520%257B%2520page%2520total_pages%2520%257D%2520&variables=%7B%22input%22%3A%7B%22filters%22%3A%5B%7B%22name%22%3A%22album_id%22%2C%22value%22%3A%22__album__id__%22%7D%5D%2C%22display%22%3A%22position%22%2C%22items_per_page%22%3A50%2C%22page%22%3A__page__number__%7D%7D'
        response = Luscious.send_request(data.replace('__album__id__', str(code)).replace('__page__number__', '1')).json()
        total_pages = response['data']['picture']['list']['info']['total_pages']
        images = [item['url_to_original'] for item in response['data']['picture']['list']['items']]
        for page in range(2,total_pages + 1):
            response = Luscious.send_request(data.replace('__album__id__', str(code)).replace('__page__number__', str(page))).json()
            new_images = [item['url_to_original'] for item in response['data']['picture']['list']['items']]
            images.extend(new_images)
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        data = 'https://apicdn.luscious.net/graphql/nobatch/?operationName=AlbumList&query=%2520query%2520AlbumList%28%2524input%253A%2520AlbumListInput%21%29%2520%257B%2520album%2520%257B%2520list%28input%253A%2520%2524input%29%2520%257B%2520info%2520%257B%2520...FacetCollectionInfo%2520%257D%2520items%2520%257B%2520...AlbumInSearchList%2520%257D%2520%257D%2520%257D%2520%257D%2520fragment%2520FacetCollectionInfo%2520on%2520FacetCollectionInfo%2520%257B%2520total_pages%2520%257D%2520fragment%2520AlbumInSearchList%2520on%2520Album%2520%257B%2520__typename%2520id%2520title%2520%257D%2520&variables=%7B%22input%22%3A%7B%22items_per_page%22%3A30%2C%22display%22%3A%22search_score%22%2C%22filters%22%3A%5B%7B%22name%22%3A%22album_type%22%2C%22value%22%3A%22manga%22%7D%2C%7B%22name%22%3A%22audience_ids%22%2C%22value%22%3A%22%2B1%2B3%2B5%22%7D%2C%7B%22name%22%3A%22language_ids%22%2C%22value%22%3A%22%2B1%2B100%2B101%2B2%2B3%2B4%2B5%2B6%2B8%2B9%2B99%22%7D%2C%7B%22name%22%3A%22search_query%22%2C%22value%22%3A%22__keyword__%22%7D%5D%2C%22page%22%3A__page__number__%7D%7D'
        total_pages = 1000
        page = 1
        while True:
            if page > total_pages:
                yield {}
            try:
                response = Luscious.send_request(data.replace('__keyword__', keyword).replace('__page__number__', str(page))).json()
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
                    'genres': genres,
                    'tags': tags,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Luscious.search_by_keyword('', False)