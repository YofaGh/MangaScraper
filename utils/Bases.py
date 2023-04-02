class Manga:
    def get_chapters():
        return []

    def get_images():
        return [], False

    def search_by_title():
        return []

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return 'Chapter 000'
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'

class Doujin:
    def get_title():
        return

    def get_images():
        return [], False

    def search_by_title():
        return []

class Req():
    def send_request(url):
        import requests
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            if response.status_code == 404:
                raise Exception('Not found')
            elif response.status_code == 403:
                raise Exception('Forbidden')
            elif response.status_code == 500:
                raise Exception('Server Error')
            else:
                raise Exception
        except Exception as e:
            raise Exception(f'Connection error: {str(e)}')