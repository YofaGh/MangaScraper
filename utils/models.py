class Module:
    domain = ''

    def send_request(url):
        import requests
        from utils.assets import waiter
        while True:
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                waiter()

    def download_image(url, image_name, log_num):
        import requests
        from termcolor import colored
        from utils.assets import waiter
        while True:
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(image_name, 'wb') as image:
                    image.write(response.content)
                return
            except (requests.exceptions.HTTPError) as error:
                print(colored(f' Warning: Could not download image {log_num}: {url}', 'red'))
                return
            except (requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                waiter()

    def get_images():
        return [], False

class Manga(Module):
    def get_chapters():
        return []

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
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

class Doujin(Module):
    def get_title():
        return ''