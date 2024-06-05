from utils.models import Doujin

class Nhentai_Net(Doujin):
    domain = 'nhentai.net'
    logo = 'https://static.nhentai.net/img/logo.090da3be7b51.svg'

    def get_info(code):
        response = Nhentai_Net.send_request(f'https://cubari.moe/read/api/nhentai/series/{code}/').json()
        images = list(list(response['chapters'].values())[0]['groups'].values())[0]
        return {
            'Cover': response['cover'],
            'Title': response['title'],
            'Pages': len(images),
            'Extras': {
                'Artists': response['artist'],
                'Authors': response['author'],
                'Groups': list(response['groups'].values()),
                'Description': response['description'],
            },
        }

    def get_title(code):
        response = Nhentai_Net.send_request(f'https://cubari.moe/read/api/nhentai/series/{code}/').json()
        return response['title']

    def get_images(code):
        response = Nhentai_Net.send_request(f'https://cubari.moe/read/api/nhentai/series/{code}/').json()
        images = list(response['chapters'].values())[0]['groups']
        return list(images.values())[0], False