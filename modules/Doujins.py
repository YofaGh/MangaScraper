from bs4 import BeautifulSoup
from utils.models import Doujin

class Doujins(Doujin):
    domain = 'doujins.com'
    logo = 'https://doujins.com/img/logo32x32.png'
    is_coded = False

    def get_info(code):
        from datetime import datetime
        from contextlib import suppress
        response, _ = Doujins.send_request(f'https://doujins.com/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        cover, title, tags, artists, pages, translated_by, uploaded = 7 * ['']
        with suppress(Exception):
            cover = soup.find('img', {'class': 'doujin active'})['data-file'].replace('&amp;', '&')
        with suppress(Exception):
            title = soup.find('div', {'class', 'folder-title'}).find_all('a')[-1].get_text(strip=True)
        with suppress(Exception):
            artists = [a.get_text(strip=True) for a in soup.find('div', {'class': 'gallery-artist'}).find_all('a')]
        with suppress(Exception):
            tags = [a.get_text(strip=True) for a in soup.find('li', {'class': 'tag-area'}).find_all('a')]
        with suppress(Exception):
            pages = soup.find_all('div', {'class': 'folder-message'})[1].get_text(strip=True).split('•')[-1].replace('images', '').strip()
        with suppress(Exception):
            uploaded = soup.find_all('div', {'class': 'folder-message'})[1].get_text(strip=True).split('•')[0].strip()
        with suppress(Exception):
            translated_by = soup.find('div', {'class': 'folder-message'}).get_text(strip=True).replace('Translated by: ', '')
        return {
            'Cover': cover,
            'Title': title,
            'Pages': pages,
            'Extras': {
                'Artists': artists,
                'Tags': tags,
                'Translated by': translated_by
            },
            'Dates': {
                'Uploaded': datetime.strptime(uploaded, '%B %dth, %Y').strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    def get_title(code):
        response, _ = Doujins.send_request(f'https://doujins.com/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'class', 'folder-title'}).find_all('a')[-1].get_text(strip=True)
        return title

    def get_images(code):
        response, _ = Doujins.send_request(f'https://doujins.com/{code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        if 'Upgrade to premium now!' in soup.find('div', {'id', 'thumbnails'}).get_text():
            return [], False
        images = soup.find_all('img', {'class': 'doujin active'})
        images = [image['data-file'].replace('&amp;', '&') for image in images]
        save_names = [f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}' for i in range(len(images))]
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        session = None
        while True:
            response, session = Doujins.send_request(f'https://doujins.com/searches?words={keyword}&page={page}', session=session)
            soup = BeautifulSoup(response.text, 'html.parser')
            divs = soup.select('#content > div > div:nth-child(5)')[0]
            try:
                divs.find_all('div', {'class': 'col-6 col-sm-4 col-md-3 col-lg-2 px-1'})[0].find('img')['srcset']
            except Exception:
                divs = soup.select('#content > div > div:nth-child(4)')[0]
            doujins = divs.find_all('div', {'class': 'col-6 col-sm-4 col-md-3 col-lg-2 px-1'})
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                tilink = doujin.find('a')
                if absolute and keyword.lower() not in tilink.get_text(strip=True).lower():
                    continue
                artist = ''
                with suppress(Exception):
                    artist = doujin.find_all(lambda tag:tag.name == 'div' and 'Artist: ' in tag.text)[-1].get_text(strip=True)
                results[tilink.get_text(strip=True)] = {
                    'domain': Doujins.domain,
                    'code': tilink['href'][1:],
                    'thumbnail': doujin.find('img')['srcset'],
                    'artists': artist.replace('Artist: ', ''),
                    'page': page
                }
            yield results
            page += 1