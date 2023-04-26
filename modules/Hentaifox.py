from bs4 import BeautifulSoup
from utils.models import Doujin

class Hentaifox(Doujin):
    domain = 'hentaifox.com'

    def get_title(code):
        response = Hentaifox.send_request(f'https://hentaifox.com/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'info'}).find('h1').contents[0]
        return title

    def get_images(code):
        response = Hentaifox.send_request(f'https://hentaifox.com/gallery/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        sample = soup.find('div', {'class': 'gallery_thumb'}).find('img')['data-src'] 
        sample_path = sample.rsplit('/', 1)[0]
        sample_format = sample.rsplit('.', 1)[1]
        pages = int(soup.find('span', {'class': 'i_text pages'}).contents[0].split(' ')[-1])
        images = [f'{sample_path}/{i}.{sample_format}' for i in range(1, pages+1)]
        return images

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Hentaifox.send_request(f'https://hentaifox.com/search/?q={keyword}&page={page}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            doujins = soup.find_all('div', {'class': 'thumb'})
            if len(doujins) == 0:
                yield {}
            results = {}
            for doujin in doujins:
                caption = doujin.find('div', {'class': 'caption'})
                ti = caption.find('a').contents[0]
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    'domain': Hentaifox.domain,
                    'code': caption.find('a')['href'].split('/')[-2],
                    'category': doujin.find('a', {'class':'t_cat'}).contents[0],
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        from requests.exceptions import HTTPError
        response = Hentaifox.send_request('https://hentaifox.com/categories/')
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.find('div', {'class': 'list_tags'}).find_all('a')
        categories = [a['href'] for a in categories]
        for category in categories:
            page = 1
            while True:
                try:
                    response = Hentaifox.send_request(f'https://hentaifox.com{category}pag/{page}/')
                except HTTPError:
                    break
                soup = BeautifulSoup(response.text, 'html.parser')
                doujins = soup.find_all('div', {'class': 'thumb'})
                if len(doujins) == 0:
                    break
                results = {}
                for doujin in doujins:
                    caption = doujin.find('div', {'class': 'caption'})
                    ti = caption.find('a').contents[0]
                    results[ti] = {
                        'domain': Hentaifox.domain,
                        'code': caption.find('a')['href'].split('/')[-2],
                        'category': doujin.find('a', {'class':'t_cat'}).contents[0]
                    }
                yield results
                page += 1
        yield {}
    
    def download_image(url, image_name, log_num):
        import requests
        from termcolor import colored
        from utils.assets import waiter
        while True:
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(image_name, 'wb') as image:
                    image.write(response.content)
                return image_name
            except (requests.exceptions.HTTPError) as error:
                break
            except (requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                waiter()
        for format in ['png', 'jpg', 'jpeg', 'gif', 'tif', 'webp']:
            while True:
                try:
                    response = requests.get(f'{url.rsplit(".", 1)[0]}.{format}')
                    response.raise_for_status()
                    with open(f'{image_name.rsplit(".", 1)[0]}.{format}', 'wb') as image:
                        image.write(response.content)
                    return f'{image_name.rsplit(".", 1)[0]}.{format}'
                except (requests.exceptions.HTTPError) as error:
                    break
                except (requests.exceptions.Timeout) as error:
                    raise error
                except requests.exceptions.RequestException:
                    waiter()
        print(colored(f' Warning: Could not download image {log_num}: {url}', 'red'))
        return ''