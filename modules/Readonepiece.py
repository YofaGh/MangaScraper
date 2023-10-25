from bs4 import BeautifulSoup
from utils.models import Manga

class Readonepiece(Manga):
    domain = 'readonepiece.com'
    logo = 'https://ww9.readonepiece.com/apple-touch-icon.png'

    def get_chapters(manga, wait=True):
        response = Readonepiece.send_request(f'https://ww9.readonepiece.com/manga/{manga}/', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'bg-bg-secondary p-3 rounded mb-3 shadow'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        chapters_urls = [chapter.replace(f'{manga}-','') for chapter in chapters]
        chapters = [{
            'url': chapter_url,
            'name': Readonepiece.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter, wait=True):
        chapter_url = chapter['url']
        if f'{manga}-' in chapter_url:
            chapter_url = chapter_url.replace(f'{manga}-','')
        response = Readonepiece.send_request(f'https://ww9.readonepiece.com/chapter/{manga}-{chapter_url}', wait=wait)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', {'class', 'mb-3 mx-auto js-page'})
        images = [image['src'] for image in images]
        return images, False