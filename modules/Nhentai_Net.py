from utils.models import Doujin

class Nhentai_Net(Doujin):
    domain = 'nhentai.net'
    logo = 'https://static.nhentai.net/img/logo.090da3be7b51.svg'

    def get_info(code):
        response, _ = Nhentai_Net.send_request(f'https://cubari.moe/read/api/nhentai/series/{code}/')
        info = response.json()
        images = list(list(info['chapters'].values())[0]['groups'].values())[0]
        return {
            'Cover': info['cover'],
            'Title': info['title'],
            'Pages': len(images),
            'Extras': {
                'Artists': info['artist'],
                'Authors': info['author'],
                'Groups': list(info['groups'].values()),
                'Description': info['description'],
            },
        }

    def get_title(code):
        response, _ = Nhentai_Net.send_request(f'https://cubari.moe/read/api/nhentai/series/{code}/')
        return response.json()['title']

    def get_images(code):
        response, _ = Nhentai_Net.send_request(f'https://cubari.moe/read/api/nhentai/series/{code}/')
        images = list(response.json()['chapters'].values())[0]['groups']
        return list(images.values())[0], False