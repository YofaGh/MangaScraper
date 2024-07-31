import requests

class Module:
    type = __qualname__
    logo = None
    domain = None
    download_images_headers = None

    @staticmethod
    def send_request(url, method='GET', session=None, **kwargs) -> tuple[requests.Response, requests.Session]:
        from utils.assets import waiter
        if kwargs.get('verify') is False:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        session = requests.Session() if not session else session
        while True:
            try:
                response = session.request(url=url, method=method, **kwargs)
                response.raise_for_status()
                return response, session
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException as error:
                waiter()

    @classmethod
    def download_image(cls, url, image_name, session=None, verify=None) -> str | None:
        try:
            response, _ = cls.send_request(url, session=session, headers=cls.download_images_headers, verify=verify)
            with open(image_name, 'wb') as image:
                image.write(response.content)
                return image_name
        except:
            return None

    def get_info() -> dict:
        return {}

    def get_images() -> tuple[list[str], bool | list[str]]:
        return [], False

class Manga(Module):
    type = __qualname__

    def get_chapters() -> list[dict]:
        return []

    def rename_chapter(chapter) -> str:
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
        new_name = new_name.rstrip('.')
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'

class Doujin(Module):
    type = __qualname__
    is_coded = True

    def get_title() -> str:
        return ''