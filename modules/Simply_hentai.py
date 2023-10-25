from bs4 import BeautifulSoup
from utils.models import Doujin

class Simply_hentai(Doujin):
    domain = 'simply-hentai.com'
    logo = 'https://www.simply-hentai.com/images/logo.svg'
    headers = {'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)'}

    def get_title(code, wait=True):
        response = Simply_hentai.send_request(f'https://www.simply-hentai.com/{code}', headers=Simply_hentai.headers, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('section', {'class', 'album-info'}).find('h1').get_text(strip=True)
        return title

    def get_images(code, wait=True):
        import json
        headers = {'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)'}
        response = Simply_hentai.send_request(f'https://www.simply-hentai.com/{code}/all-pages', headers=Simply_hentai.headers, wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'}).get_text(strip=True)
        data_raw = json.loads(script)
        images = [image['sizes']['full'] for image in data_raw['props']['pageProps']['data']['pages']]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute, wait=True):
        page = 1
        while True:
            response = Simply_hentai.send_request(f'https://api.simply-hentai.com/v3/search/complex?filter[class_name][0]=Manga&query={keyword}&page={page}', headers=Simply_hentai.headers, wait=wait)
            datas = response.json()['data']
            if len(datas) == 0:
                yield {}
            results = {}
            for data in datas:
                doujin = data['object']
                if absolute and keyword.lower() not in doujin['title'].lower():
                    continue
                results[doujin['title']] = {
                    'domain': Simply_hentai.domain,
                    'code': f'{doujin["series"]["slug"]}/{doujin["slug"]}',
                    'thumbnail': doujin['preview']['sizes']['thumb'],
                    'page': page
                }
            page += 1
            yield results

    def get_db(wait=True):
        page = 1
        prev_page = None
        while True:
            response = Simply_hentai.send_request(f'https://www.simply-hentai.com/2-mangas/page-{page}', headers=Simply_hentai.headers, wait=wait)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = {}
            divs = soup.find_all('div', {'class', 'col-6 col-lg-3'})
            if divs == prev_page:
                yield {}
            for div in divs:
                doujin = div.find('div', {'class', 'info'})
                tilink = doujin.find('a')
                language = doujin.find('a', {'class', 'is-trigger ism-trigger'})['href'].split('/')[-1]
                number_of_pages = doujin.find('div', {'class', 'col-8 text-right count-col'}).get_text(strip=True)
                results[tilink.get_text(strip=True)] = {
                    'domain': Simply_hentai.domain,
                    'code': tilink['href'][1:],
                    'language': language,
                    'number_of_pages': number_of_pages,
                    'page': page
                }
            page += 1
            yield results
            prev_page = divs