from bs4 import BeautifulSoup
from utils.models import Manga

class Bato(Manga):
    domain = 'bato.to'
    logo = 'https://bato.to/public-assets/img/favicon.ico'

    def get_chapters(manga):
        response = Bato.send_request(f'https://bato.to/title/{manga}')
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('div', {'class': 'group flex flex-col-reverse'}).find_all('a', {'class': 'link-hover link-primary visited:text-accent'})
        chapters_urls = [link['href'].split('/')[-1] for link in links]
        chapters = [{
            'url': chapter_url,
            'name': Bato.rename_chapter(chapter_url)
        } for chapter_url in chapters_urls]
        return chapters

    def get_images(manga, chapter):
        import json
        response = Bato.send_request(f'https://bato.to/chapter/{chapter["url"].split("-")[0]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find(lambda tag:tag.name == 'script' and 'imgHttpLis' in tag.text).text
        vars = script.split('\n')
        images = json.loads(vars[5].split('= ', 1)[1][:-1])
        password_raw = vars[6].split('= ', 1)[1][:-1]
        encrypted_tokens = vars[7].split('= "', 1)[1][:-2]
        password = Bato._normalize_pass(password_raw)
        tokens = json.loads(Bato._decrypt_tokens(encrypted_tokens, password))
        images = [f'{url}?{tail}' for url, tail in zip(images, tokens)]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError
        page = 1
        while True:
            try:
                response = Bato.send_request(f'https://bato.to/v3x-search?word={keyword}&page={page}')
            except HTTPError:
                yield {}
            soup = BeautifulSoup(response.text, 'html.parser')
            mangas = soup.find_all('div', {'class': 'flex border-b border-b-base-200 pb-5'})
            if len(mangas) == 0:
                yield {}
            results = {}
            for index, manga in enumerate(mangas):
                ti = manga.find('h3').find('a')
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                alias, genres, latest_chapter = '', '', ''
                with suppress(Exception): alias = manga.find('div', {'data-hk': f'0-0-3-{index}-4-0'}).get_text(strip=True)
                with suppress(Exception): genres = manga.find('div', {'data-hk': f'0-0-3-{index}-6-0'}).get_text(strip=True)
                with suppress(Exception): latest_chapter = manga.find('div', {'data-hk': f'0-0-3-{index}-7-1-0-0'}).find('a')['href'].split('/')[-1]
                results[ti.get_text(strip=True)] = {
                    'domain': Bato.domain,
                    'url': ti['href'].replace('/title/', ''),
                    'latest_chapter': latest_chapter,
                    'thumbnail': manga.find('img')['src'],
                    'genres': genres,
                    'alias': alias,
                    'page': page
                }
            yield results
            page += 1

    def get_db():
        return Bato.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        chap = chapter.split('-', 1)[1] if '-' in chapter else chapter
        new_name = ''
        reached_number = False
        for ch in chap:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chap
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'

    def _normalize_pass(pass_raw):
        gg = pass_raw.replace('!+[]', '$').replace('[+[]]', '[]').replace('+', '')
        start_of_dot = gg.find('(')
        end_of_dot = gg.rfind(')')
        gg  = f'{gg[:start_of_dot]}{gg[end_of_dot+4:]}'
        gg = gg.split(']')
        gg = [str(g.count('$')) for g in gg[:-1]]
        gg = ''.join(gg)
        return gg[:8]+'.'+gg[8:]

    def _decrypt_tokens(encrypted_tokens, password):
        import base64
        from hashlib import md5
        from Crypto.Cipher import AES
        def _bytes_to_key(salt, password):
            dtot = md5(password+salt).digest()
            d = [dtot]
            while len(dtot)<48:
                d.append(md5(d[-1]+password+salt).digest())
                dtot += d[-1]
            return dtot[:32], dtot[32:]
        unpad = lambda s: s[:-ord(s[-1:])]
        encrypted = base64.b64decode(encrypted_tokens)
        salt = encrypted[8:16]
        ciphertext = encrypted[16:]
        key, iv = _bytes_to_key(salt, password.encode())
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext)).decode('utf-8')