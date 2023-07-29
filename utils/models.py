class Module:
    domain = ''
    download_images_headers = None

    @classmethod
    def send_request(self, url, method='GET', headers=None, json=None, data=None, verify=None):
        import requests
        if verify is False:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        while True:
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, json=json, data=data, verify=verify)
                elif method == 'POST':
                    response = requests.post(url, headers=headers, json=json, data=data, verify=verify)
                response.raise_for_status()
                return response
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                self._waiter()

    @classmethod
    def download_image(self, url, image_name, log_num, headers=None):
        from requests.exceptions import HTTPError, Timeout
        from termcolor import colored
        while True:
            try:
                response = self.send_request(url, headers=headers)
                with open(image_name, 'wb') as image:
                    image.write(response.content)
                return image_name
            except HTTPError as error:
                print(colored(f' Warning: Could not download image {log_num}: {url}', 'red'))
                return ''
            except Timeout as error:
                raise error

    def _waiter():
        import shutil, time, sys
        from termcolor import colored
        sys.stdout.write(colored(' Connection lost.\n\rWaiting 1 minute to attempt a fresh connection.', 'red'))
        for i in range(59, 0, -1):
            time.sleep(1)
            sys.stdout.write(colored(f'\rWaiting {i} seconds to attempt a fresh connection. ', 'red'))
        sys.stdout.write(f'\r{" " * shutil.get_terminal_size()[0]}')

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