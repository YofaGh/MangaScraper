import argparse

class SetSource(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        from utils.modules_contributer import contributer
        values = contributer(values)
        setattr(namespace, self.dest, values)

class LastChapter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 0:
            raise ValueError('Minimum chapter is 0')
        if values.is_integer():
            values = int(values)
        setattr(namespace, self.dest, values)

class RangeOfChapters(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values[0] > values[1]:
            raise ValueError('The beginning chapter must be lower than the ending chapter')
        for i in range(len(values)):
            if values[i] < 0:
                raise ValueError('Minimum chapter is 0')
            if values[i].is_integer():
                values[i] = int(values[i])
        setattr(namespace, self.dest, values)

class CheckChapters(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        for i in range(len(values)):
            if values[i].is_integer():
                values[i] = int(values[i])
        setattr(namespace, self.dest, values)

def validate_corrupted_image(path_to_image):
    from PIL import Image
    try:
        im = Image.open(path_to_image)
        im.verify()
        im.close()
        return True
    except:
        return False

def validate_truncated_image(path_to_image):
    from PIL import Image
    try:
        Image.open(path_to_image).load()
        return True
    except:
        return False

def validate_folder(path_to_folder):
    images_path = detect_images(path_to_folder)
    for image_path in images_path:
        if not (validate_corrupted_image(image_path) and validate_truncated_image(image_path)):
            return False
    return True

def create_folder(folder):
    import os
    os.mkdir(folder) if not os.path.exists(folder) else None

def create_path(path):
    import os
    folders = list(filter(None, path.split('/')))
    temp_path = ''
    for folder in folders:
        temp_path = os.path.join(temp_path, folder)
        create_folder(temp_path)

def fix_name_for_folder(manga):
    name = ''.join([ch for ch in manga if ch not in '\/:*?"><|'])
    while name[-1] == '.':
        name = name[:-1]
    return name

def detect_images(path_to_folder):
    import os
    images_path = []
    for file in os.listdir(path_to_folder):
        if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.webp'):
            images_path.append(f'{path_to_folder}/{file}')
    return images_path

def waiter():
    import time, sys
    from termcolor import colored
    sys.stdout.write(colored(' Connection lost.\n\rWaiting 1 minute to attempt a fresh connection.', 'red'))
    for i in range(59, 0, -1):
        time.sleep(1)
        sys.stdout.write(colored(f'\rWaiting {i} seconds to attempt a fresh connection. ', 'red'))
    return