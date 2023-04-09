from bs4 import BeautifulSoup
from utils.Bases import Manga, Req

class Coloredmanga(Manga, Req):
    def get_chapters(manga):
        response = Coloredmanga.send_request(f'https://coloredmanga.com/mangas/{manga}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('li', {'class':'wp-manga-chapter'})
        chapters = [div.find('a')['href'].replace(f'https://coloredmanga.com/mangas/{manga}/', '')[:-1] for div in divs[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Coloredmanga.send_request(f'https://coloredmanga.com/mangas/{manga}/{chapter}/')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-content'}).find_all('img')
        images = [image['src'].strip() for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1]}')
        return images, save_names

    def search(title, absolute):
        page = 1
        while True:
            response = Coloredmanga.send_request(f'https://coloredmanga.com/page/{page}/?s={title}&post_type=wp-manga')
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'post-title'})
            results = []
            for manga in mangas:
                if absolute and title.lower() not in manga.find('a')['href']:
                    continue
                results.append(f'title: {manga.find("a").contents[0]}, url: {manga.find("a")["href"].replace("https://coloredmanga.com/mangas/","")[:-1]}')
            yield results
            page += 1

    def rename_chapter(chapter):
        chapter = chapter.split('/')[-1]
        beginner = 'Chapter'
        if 'volume' in chapter:
            beginner = 'Volume'
        elif 'number' in chapter:
            beginner = 'Number'
        if chapter in ['pass', None]:
            return f'{beginner} 000'
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-._' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'{beginner} {int(new_name):03d}'
        except:
            return f'{beginner} {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'