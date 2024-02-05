from bs4 import BeautifulSoup
from utils.models import Doujin

class _999hentai(Doujin):
    domain = '999hentai.net'
    logo = 'https://999hentai.net/icons/icon-32x32.ico'
    headers = {'User-Agent': 'Mozilla/5.0'}
    is_coded = False

    def get_info(code, wait=True):
        from contextlib import suppress
        response = _999hentai.send_request(f'https://999hentai.net/hchapter/{code}', headers=_999hentai.headers, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, pages = '', '', ''
        extras = {}
        with suppress(Exception): 
            host = soup.find(lambda tag: tag.name == 'meta' and tag.get('property') == 'og:image')['content'].rsplit('/', 1)[0]
            cover = soup.find(lambda tag: tag.name == 'script' and '__NUXT__' in tag.text).get_text(strip=True).split('pics:[', 1)[1]
            cover = cover.split('url:"', 1)[1].split('",', 1)[0]
            cover = f'{host}/{cover}'
        with suppress(Exception): title = soup.find('h1').get_text(strip=True)
        for div in soup.find('div', {'class': 'col-md-8 col-sm-12'}).find_all('div', recursive=False):
            if 'Page' in div.text:
                with suppress(Exception): pages = div.get_text(strip=True).replace('Page:', '')
            elif 'Tags' in div.text:
                with suppress(Exception): extras['Tags'] = [a.contents[0].strip().capitalize() for a in div.find_all('a')]
            else:
                tag_name = div.find('span').get_text(strip=True)
                with suppress(Exception): extras[tag_name.rstrip(':')] = div.get_text(strip=True).replace(tag_name, '')
        return {
            'Cover': cover,
            'Title': title,
            'Pages': pages,
            'Extras': extras
        }

    def get_title(code, wait=True):
        response = _999hentai.send_request(f'https://999hentai.net/hchapter/{code}', headers=_999hentai.headers, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True)
        return title

    def get_images(code, wait=True):
        response = _999hentai.send_request(f'https://999hentai.net/hchapter/{code}', headers=_999hentai.headers, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find(lambda tag: tag.name == 'script' and '__NUXT__' in tag.text).get_text(strip=True).split('pics:[', 1)[1].split('],picsS')[0]
        images = [image.split('url:"', 1)[1].split('",', 1)[0] for image in images.split('},{')]
        host = soup.find(lambda tag: tag.name == 'meta' and tag.get('property') == 'og:image')['content'].rsplit('/', 1)[0]
        images = [f'{host}/{image}' for image in images]
        return images, False