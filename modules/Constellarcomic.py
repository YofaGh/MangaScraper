from bs4 import BeautifulSoup
from utils.models import Manga

class Constellarcomic(Manga):
    domain = 'constellarcomic.com'
    logo = 'https://constellarcomic.com/wp-content/uploads/2022/11/Constellar-Logo-Rounded-000.png'
    headers = {'User-Agent': 'Leech/1051 CFNetwork/454.9.4 Darwin/10.3.0 (i386) (MacPro1%2C1)'}

    def get_chapters(manga):
        response = Constellarcomic.send_request(f'https://constellarcomic.com/manga/{manga}/', headers=Constellarcomic.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('div', {'id': 'chapterlist'}).find_all('a')
        chapters_urls = [link['href'].split('/')[-2].replace(f'{manga}-', '') for link in links[::-1]]
        chapters = [{
            'url': chapter_url,
            'name': Constellarcomic.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        import json
        chapter_url = chapter['url']
        if f'{manga}-' in chapter_url:
            chapter_url = chapter_url.replace(f'{manga}-', '')
        response = Constellarcomic.send_request(f'https://constellarcomic.com/{manga}-{chapter_url}/', headers=Constellarcomic.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag:tag.name == 'script' and 'NO IMAGE YET' in tag.text)
        images = json.loads(script.get_text(strip=True).replace('ts_rea_der_._run(', '')[:-2])
        images = images['sources'][0]['images']
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        while True:
            response = Constellarcomic.send_request(f'https://constellarcomic.com/page/{page}/?s={keyword}', headers=Constellarcomic.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'bs swiper-slide'})
            if len(mangas) == 0 or response.url == f'https://constellarcomic.com/?s={keyword}':
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find('a')
                if absolute and keyword.lower() not in ti['title'].lower():
                    continue
                status = ''
                with suppress(Exception): status = ti.find('i').get_text(strip=True)
                results[ti['title']] = {
                    'domain': Constellarcomic.domain,
                    'url': ti['href'].split('/')[-2],
                    'thumbnail': manga.find('img')['src'],
                    'status': status,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Constellarcomic.search_by_keyword('', False)