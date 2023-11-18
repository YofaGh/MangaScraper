from PIL import Image
from shutil import copy2
from utils.logger import log_over, log, clear
from utils.assets import validate_folder, detect_images, create_folder
from settings import FIT_MERGE

def merge_folder(path_to_source, path_to_destination, name=None):
    name = name if name else path_to_source
    if not validate_folder(path_to_source):
        log(f'\rFailed to Merge {path_to_source} because one image is corrupted or truncated.', 'red')
        return
    create_folder(path_to_destination)
    images_path = detect_images(path_to_source)
    if not images_path:
        log(f'\rFailed to Merge {path_to_source} because there was no image in the given folder.', 'red')
        return
    images = [Image.open(image_path) for image_path in images_path]
    if FIT_MERGE:
        log_over(f'\r{name}: Merging with resizing enabled, overall quality might get reduced during the proccess...')
        results = merge_fit(images, path_to_destination)
    else:
        log_over(f'\r{name}: Merging without resizing, You might see white spaces around some images...')
        results = merge(images, path_to_destination)
    clear()
    log(f'\r{name}: Merged {len(images_path)} images into {results}.', 'green')

def merge(images, path_to_destination):
    lists_to_merge = []
    temp_list = []
    temp_height = 0
    for image in images:
        if (temp_height + image.height) < 65500:
            temp_list.append(image)
            temp_height += image.height
        else:
            lists_to_merge.append(temp_list)
            temp_list = [image]
            temp_height = image.height
    lists_to_merge.append(temp_list)
    for index, list_to_merge in enumerate(lists_to_merge):
        if len(list_to_merge) == 1:
            copy2(list_to_merge[0].filename, f'{path_to_destination}/{index+1:03d}.{list_to_merge[0].filename.split(".")[-1]}')
            continue
        widths, heights = zip(*(image.size for image in list_to_merge))
        total_height = sum(heights)
        max_width = max(widths)
        merged_image = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))
        x_offset = 0
        for image in list_to_merge:
            merged_image.paste(image, (int((max_width - image.width)/2), x_offset))
            x_offset += image.height
        merged_image.save(f'{path_to_destination}/{index+1:03d}.jpg')
    return len(lists_to_merge)

def merge_fit(images, path_to_destination):
    import math
    lists_to_merge = []
    min_width = images[0].width
    current_height = 0
    temp_list = []
    for image in images:
        if image.width == min_width:
            if (current_height + image.height) < 65500:
                temp_list.append(image)
                current_height = current_height + image.height
            else:
                lists_to_merge.append(temp_list)
                temp_list = [image]
                current_height = image.height
        elif image.width > min_width:
            if (current_height + image.height * min_width / image.width) < 65500:
                temp_list.append(image)
                current_height = current_height + image.height * min_width / image.width
            else:
                lists_to_merge.append(temp_list)
                temp_list = [image]
                min_width = image.width
                current_height = image.height
        else:
            if (current_height * image.width / min_width + image.height) < 65500:
                temp_list.append(image)
                current_height = current_height * image.width / min_width + image.height
                min_width = image.width
            else:
                lists_to_merge.append(temp_list)
                temp_list = [image]
                min_width = image.width
                current_height = image.height
    lists_to_merge.append(temp_list)
    for index, list_to_merge in enumerate(lists_to_merge):
        if len(list_to_merge) == 1:
            copy2(list_to_merge[0].filename, f'{path_to_destination}/{index+1:03d}.{list_to_merge[0].filename.split(".")[-1]}')
            continue
        min_width = min(list_to_merge, key=lambda image: image.width).width
        total_height = 0
        for image in list_to_merge:
            total_height += image.height * min_width / image.width
        merged_image = Image.new('RGB', (min_width, math.ceil(total_height)), color=(255, 255, 255))
        x_offset = 0
        for image in list_to_merge:
            image.thumbnail((min_width, image.height*(min_width/image.width)), Image.Resampling.LANCZOS)
            merged_image.paste(image, (0, x_offset))
            x_offset += image.height
        merged_image.save(f'{path_to_destination}/{index+1:03d}.jpg')
    return len(lists_to_merge)

def merge_bulk(path_to_source, path_to_destination):
    import os
    sub_folders = os.listdir(path_to_source)
    for sub_folder in sub_folders:
        merge_folder(f'{path_to_source}/{sub_folder}', f'{path_to_destination}/{sub_folder}', f'{path_to_source}: {sub_folder}')