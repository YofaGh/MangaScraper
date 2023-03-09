from utils.Bases import Manga, Req
from bs4 import BeautifulSoup

class Readonepiece(Manga, Req):
    def get_chapters(manga):
        response = Readonepiece.send_request(f'https://ww9.readonepiece.com/manga/{manga}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'bg-bg-secondary p-3 rounded mb-3 shadow'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        chapters = [chapter.replace(f'{manga}-','') for chapter in chapters]
        return chapters

    def get_images(manga, chapter):
        response = Readonepiece.send_request(f'https://ww9.readonepiece.com/chapter/{manga}-{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', {'class', 'mb-3 mx-auto js-page'})
        images = [image['src'] for image in images]
        return images, False