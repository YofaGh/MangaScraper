import argparse, sys, os
from utils import assets
from termcolor import colored
from PIL import Image

def merge_folder(path_to_source, path_to_destination):
    if not assets.validate_folder(path_to_source):
        print(colored(f'\rFailed to Merge {path_to_source} because one image is corrupted or truncated.', 'red'))
        return [], []
    assets.create_path(path_to_destination)
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
    return images_path, lists_to_merge

def merge_chapter(manga, chapter):
    fixed_manga = assets.fix_name_for_folder(manga)
    if not assets.validate_folder(f'{fixed_manga}/{chapter}'):
        print(colored(f'\r{manga}: Failed to Merge {chapter} because one image is corrupted or truncated.', 'red'))
        return
    assets.create_path(f'Merged/{fixed_manga}/{chapter}')
    sys.stdout.write(f'\r{manga}: Merging {chapter}...')
    images_path, lists_to_merge = merge_folder(f'{fixed_manga}/{chapter}', f'Merged/{fixed_manga}/{chapter}')
    print(colored(f'\r{manga}: Merged {len(images_path)} images of {chapter} into {len(lists_to_merge)}.', 'green'))

def merge_manga(manga):
    chapters = os.listdir(assets.fix_name_for_folder(manga))
    for chapter in chapters:
        merge_chapter(manga, chapter)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(allow_abbrev=False)
    merging_options = parser.add_mutually_exclusive_group()
    merging_options.add_argument('-mergefolder', action='store', help='merges images in given folder')
    merging_options.add_argument('-mergechapter', action='store', help='merges given chapter')
    merging_options.add_argument('-mergemanga', action='store', help='merges all chapters of given manga')
    parser.add_argument('-c', action=assets.CheckChapters, nargs='+', type=float, help='specifie chapters')
    args = parser.parse_args()
    if args.mergechapter and not args.c:
        parser.error('please specify chapter alongside the manga folder with -c argument')
    os.system('color')
    if args.mergechapter:
        for chapter in args.c:
            merge_chapter(args.mergechapter, chapter)
    elif args.mergemanga:
        merge_manga(args.mergemanga)
    elif args.mergefolder:
        merge_folder(args.mergefolder, f'Merged/{args.mergefolder}')
    else:
        parser.error('at least one argument is required')