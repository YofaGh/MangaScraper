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
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        page = 1
        while True:
            try:
                response = Hentaifox.send_request(f'https://hentaifox.com/search/?q={keyword}&page={page}')
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
            except HTTPError:
                yield {}
            except Timeout as error:
                raise error
            except RequestException:
                waiter()

    def get_db():
        from utils.assets import waiter
        from requests.exceptions import RequestException, HTTPError, Timeout
        response = Hentaifox.send_request('https://hentaifox.com/categories/')
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.find('div', {'class': 'list_tags'}).find_all('a')
        categories = [a['href'] for a in categories]
        for category in categories:
            page = 1
            while True:
                try:
                    response = Hentaifox.send_request(f'https://hentaifox.com{category}pag/{page}/')
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
                except HTTPError:
                    break
                except Timeout as error:
                    raise error
                except RequestException:
                    waiter()
        yield {}