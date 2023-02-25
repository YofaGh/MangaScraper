from utils.Bases import Manga, Req
from bs4 import BeautifulSoup

class Readonepiece(Manga, Req):
    def get_chapters(*argv):
        response = Readonepiece.send_request('https://ww9.readonepiece.com/manga/one-piece-digital-colored-comics/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'bg-bg-secondary p-3 rounded mb-3 shadow'})
        chapters = [div.find('a')['href'].split('/')[-1] for div in divs[::-1]]
        return chapters

    def get_images(*argv):
        response = Readonepiece.send_request(f'https://ww9.readonepiece.com/chapter/{argv[1]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', {'class', 'mb-3 mx-auto js-page'})
        images = [image['src'] for image in images]
        return images, False