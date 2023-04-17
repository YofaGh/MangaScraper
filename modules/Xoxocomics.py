from bs4 import BeautifulSoup
from utils.Bases import Comic

class Xoxocomics(Comic):
    def get_chapters(comic):
        page = 1
        issues = []
        while True:
            response = Xoxocomics.send_request(f'https://xoxocomics.com/comic/{comic}?page={page}')
            soup = BeautifulSoup(response.text, 'html.parser')
            divs = soup.find_all('div', {'class': 'col-xs-9 chapter'})
            if len(divs) == 0:
                break
            issues = [div.find('a')['href'].replace(f'https://xoxocomics.com/comic/{comic}/', '') for div in divs[::-1]] + issues
            page += 1
        return issues

    def get_images(comic, issue):
        response = Xoxocomics.send_request(f'https://xoxocomics.com/comic/{comic}/{issue}/all')
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', {'class': 'reading-detail box_doc'}).find_all('div', {'class': 'page-chapter'})
        images = [image.find('img')['data-original'].strip() for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.jpg')
        return images, save_names
    
    def download_image(url, path, name):
        response = Xoxocomics.send_request(url)
        file_original_name = response.headers['Content-Disposition'].split('\"')[-2]
        file_format = file_original_name.split('.')[-1]
        new_name = f'{name.rsplit(".", 1)[0]}.{file_format}'
        with open(f'{path}/{new_name}', 'wb') as image:
            image.write(response.content)
    
    def rename_chapter(issue):
        if issue in ['pass', None]:
            return ''
        issue = issue.split('/')[0]
        new_name = ''
        reached_number = False
        for ch in issue:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return issue
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Issue #{int(new_name):03d}'
        except:
            return f'Issue #{new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'