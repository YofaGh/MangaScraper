from bs4 import BeautifulSoup
from utils.models import Manga

class Toonily(Manga):
    domain = 'toonily.com'
    download_images_headers = {'Referer': 'https://toonily.com/'}
    search_headers = {'cookie': 'toonily-mature=1'}

    def get_chapters(manga):
        response = Toonily.send_request(f'https://toonily.com/webtoon/{manga}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class': 'wp-manga-chapter'})
        chapters = [div.find('a')['href'].split('/')[-2] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Toonily.send_request(f'https://toonily.com/webtoon/{manga}/{chapter}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['data-src'].strip() for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        template = f'https://toonily.com/search/{keyword}/page/P_P_P_P/' if keyword else f'https://toonily.com/search/page/P_P_P_P/'
        page = 1
        while True:
            try:
                response = Toonily.send_request(template.replace('P_P_P_P', str(page)), headers=Toonily.search_headers)
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'item-summary'})
            results = {}
            for manga in mangas:
                ti = manga.find('a').text
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    'domain': Toonily.domain,
                    'url': manga.find('a')['href'].split('/')[-2],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Toonily.search_by_keyword('', False)

    def download_image(url, image_name, log_num):
        import requests
        from termcolor import colored
        from utils.assets import waiter
        while True:
            try:
                response = requests.get(url, headers=Toonily.download_images_headers)
                response.raise_for_status()
                with open(image_name, 'wb') as image:
                    image.write(response.content)
                return image_name
            except (requests.exceptions.HTTPError) as error:
                print(colored(f' Warning: Could not download image {log_num}: {url}', 'red'))
                return ''
            except (requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                waiter()