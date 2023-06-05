import shutil, sys
from PIL import Image
from utils import assets
from termcolor import colored

def merge_folder(path_to_source, path_to_destination, fit_merge, name=None):
    name = name if name else path_to_source
    if not assets.validate_folder(path_to_source):
        print(colored(f'\rFailed to Merge {path_to_source} because one image is corrupted or truncated.', 'red'))
        return
    assets.create_path(path_to_destination)
    images_path = assets.detect_images(path_to_source)
    images = [Image.open(image_path) for image_path in images_path]
    if fit_merge:
        sys.stdout.write(f'\r{name}: Merging with resizing enabled, overall quality might get reduced during the proccess...')
        results = merge_fit(images, path_to_destination)
    else:
        sys.stdout.write(f'\r{name}: Merging without resizing, You might see white spaces around some images...')
        results = merge(images, path_to_destination)
    sys.stdout.write(f'\r{" " * shutil.get_terminal_size()[0]}')
    print(colored(f'\r{name}: Merged {len(images_path)} images into {results}.', 'green'))

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
    for i in range(len(lists_to_merge)):
        if len(lists_to_merge[i]) == 1:
            shutil.copy2(lists_to_merge[i][0].filename, f'{path_to_destination}/{i+1:03d}.{lists_to_merge[i][0].filename.split(".")[-1]}')
            continue
        widths, heights = zip(*(image.size for image in lists_to_merge[i]))
        total_height = sum(heights)
        max_width = max(widths)
        merged_image = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))
        x_offset = 0
        for image in lists_to_merge[i]:
            merged_image.paste(image, (int((max_width - image.size[0])/2), x_offset))
            x_offset += image.size[1]
        merged_image.save(f'{path_to_destination}/{i+1:03d}.jpg')
    return len(lists_to_merge)

def merge_fit(images, path_to_destination):
    import math
    lists_to_merge = []
    min_width = images[0].size[0]
    current_height = 0
    temp_list = []
    for image in images:
        image_width = image.size[0]
        image_height = image.size[1]
        if image_width == min_width:
            if (current_height + image_height) < 65500:
                temp_list.append(image)
                current_height = current_height + image_height
            else:
                lists_to_merge.append(temp_list)
                temp_list = [image]
                current_height = image_height
        elif image_width > min_width:
            if (current_height + image_height * min_width / image_width) < 65500:
                temp_list.append(image)
                current_height = current_height + image_height * min_width / image_width
            else:
                lists_to_merge.append(temp_list)
                temp_list = [image]
                min_width = image_width
                current_height = image_height
        else:
            if (current_height * image_width / min_width + image_height) < 65500:
                temp_list.append(image)
                current_height = current_height * image_width / min_width + image_height
                min_width = image_width
            else:
                lists_to_merge.append(temp_list)
                temp_list = [image]
                min_width = image_width
                current_height = image_height
    lists_to_merge.append(temp_list)
    for i in range(len(lists_to_merge)):
        if len(lists_to_merge[i]) == 1:
            shutil.copy2(lists_to_merge[i][0].filename, f'{path_to_destination}/{i+1:03d}.{lists_to_merge[i][0].filename.split(".")[-1]}')
            continue
        widths = [image.size[0] for image in lists_to_merge[i]]
        min_width = min(widths)
        total_height = 0
        for image in lists_to_merge[i]:
            total_height += image.size[1] * min_width / image.size[0]
        merged_image = Image.new('RGB', (min_width, math.ceil(total_height)), color=(255, 255, 255))
        x_offset = 0
        for image in lists_to_merge[i]:
            image.thumbnail((image.size[0]*(min_width/image.size[0]), image.size[1]*(min_width/image.size[0])), Image.Resampling.LANCZOS)
            merged_image.paste(image, (0, x_offset))
            x_offset += image.size[1]
        merged_image.save(f'{path_to_destination}/{i+1:03d}.jpg')
    return len(lists_to_merge)

def merge_bulk(path_to_source, path_to_destination, fit_merge):
    import os
    sub_folders = os.listdir(path_to_source)
    for sub_folder in sub_folders:
        merge_folder(f'{path_to_source}/{sub_folder}', f'{path_to_destination}/{sub_folder}', fit_merge, f'{path_to_source}: {sub_folder}')