from settings import SLEEP_TIME, MODULES_FILE_PATH

def validate_corrupted_image(path_to_image):
    from PIL import Image
    try:
        Image.open(path_to_image).verify()
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

def load_modules_yaml_file():
    import yaml
    with open(MODULES_FILE_PATH, encoding='utf8') as file:
        return yaml.safe_load(file)

def load_json_file(path_to_file):
    import json
    with open(path_to_file) as file:
        return json.load(file)

def save_json_file(path_to_file, content):
    import json
    with open(path_to_file, 'w', encoding='utf8') as file:
        json.dump(content, file, indent=4, ensure_ascii=False)

def validate_folder(path_to_folder):
    images_path = detect_images(path_to_folder)
    for image_path in images_path:
        if not (validate_corrupted_image(image_path) and validate_truncated_image(image_path)):
            return False
    return True

def create_folder(path):
    import os
    os.makedirs(path, exist_ok=True)

def fix_name_for_folder(name):
    return ''.join([ch for ch in name if ch not in r'\/:*?"><|']).rstrip('.')

def detect_images(path_to_folder):
    import os
    from natsort import os_sorted
    images_path = []
    for file in os.listdir(path_to_folder):
        if file.endswith(('jpg', 'png', 'jpeg', 'gif', 'webp')):
            images_path.append(f'{path_to_folder}/{file}')
    return os_sorted(images_path)

def sleep(secs=SLEEP_TIME):
    import time
    time.sleep(secs)

def waiter():
    from utils import logger
    logger.log_over(' Connection lost.\n\rWaiting 1 minute to attempt a fresh connection.', 'red')
    for i in range(59, 0, -1):
        sleep(1)
        logger.log_over(f'\rWaiting {i} seconds to attempt a fresh connection. ', 'red')
    logger.clear()