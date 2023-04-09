from bs4 import BeautifulSoup
from utils.Bases import Manga, Req

class Manhwa365(Manga, Req):
    def get_chapters(manga):
        response = Manhwa365.send_request(f'https://manhwa365.com/webtoon/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Manhwa365.send_request(f'https://manhwa365.com/webtoon/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class':'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        return images, False

    def search(title, absolute):
        page = 1
        while True:
            response = Manhwa365.send_request(f'https://manhwa365.com/page/{page}/?s={title}&post_type=wp-manga')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'row c-tabs-item__content'})
            results = []
            for manga in mangas:
                ti = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['title']
                link = manga.find('div', {'class': 'tab-thumb c-image-hover'}).find('a')['href'].split('/')[-2]
                if absolute and title.lower() not in ti.lower():
                    continue
                results.append(f'title: {ti}, url:{link}')
            yield results
            page += 1