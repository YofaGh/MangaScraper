import sys, os
from termcolor import colored
from utils import assets
from PIL import Image

def merge_folder(path_to_source, path_to_destination, name=None):
    name = name if name else path_to_source
    if not assets.validate_folder(path_to_source):
        print(colored(f'\rFailed to Merge {path_to_source} because one image is corrupted or truncated.', 'red'))
        return
    assets.create_path(path_to_destination)
    sys.stdout.write(f'\r{name}: Merging...')
    images_path = assets.detect_images(path_to_source)
    images = [Image.open(image_path) for image_path in images_path]
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
        ## !!!! This condition is yet to be fully tested !!!! ##
        if len(lists_to_merge[i]) == 1:
            lists_to_merge[i][0].save(f'{path_to_destination}/{i+1:03d}.{lists_to_merge[i][0].filename.split(".")[-1]}')
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
    print(colored(f'\r{name}: Merged {len(images_path)} images into {len(lists_to_merge)}.', 'green'))

def merge_bulk(path_to_source, path_to_destination):
    sub_folders = os.listdir(path_to_source)
    for sub_folder in sub_folders:
        merge_folder(f'{path_to_source}/{sub_folder}', f'{path_to_destination}/{sub_folder}', f'{path_to_source}: {sub_folder}')