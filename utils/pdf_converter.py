import argparse, img2pdf, sys, os
from utils import assets
from termcolor import colored

def convert_folder(path_to_source, path_to_destination, name):
    if not assets.validate_folder(path_to_source):
        print(colored(f'\rFailed to convert {path_to_source} because of a corrupted image.', 'red'))
        return
    assets.create_path(path_to_destination)
    images_path = assets.detect_images(path_to_source)
    with open(os.path.join(path_to_destination, name), 'wb') as pdf_file:
        pdf_file.write(img2pdf.convert(images_path))

def convert_chapter(path_to_source, manga, chapter, path_to_destination):
    if not assets.validate_folder(path_to_source):
        print(colored(f'\rFailed to convert {path_to_source} because of a corrupted image.', 'red'))
        return
    sys.stdout.write(f'\r{manga}: Converting {chapter} to pdf...')
    convert_folder(path_to_source, path_to_destination, f'{manga}_{chapter}.pdf')
    print(colored(f'\r{manga}: Converted {chapter} to pdf.      ', 'green'))

def convert_manga(path_to_source, manga, path_to_destination, chapters):
    for chapter in chapters:
        convert_chapter(path_to_source, manga, chapter, path_to_destination)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(allow_abbrev=False)
    merging_options = parser.add_mutually_exclusive_group()
    merging_options.add_argument('-folder2pdf', action='store', help='converts images in given folder to pdf')
    merging_options.add_argument('-manga2pdf', action='store', help='converts all chapters of given manga to pdf')
    parser.add_argument('-dpath', action='store', help='specify a path')
    parser.add_argument('-spath', action='store', required=True, help='specify path of source')
    chapters_to_merge = parser.add_mutually_exclusive_group()
    chapters_to_merge.add_argument('-c', action=assets.CheckChapters, nargs='+', type=float, help='specifie chapters')
    chapters_to_merge.add_argument('-a', action='store_true', help='converts all chapters')
    parser.add_argument('-n', action='store', help='specify name of pdf')
    args = parser.parse_args()
    if args.folder2pdf and not args.n:
        parser.error('please specify a name for pdf')
    os.system('color')
    if args.manga2pdf:
        if args.a:
            convert_manga(args.spath, args.manga2pdf, args.dpath, os.listdir(f'{args.spath}/{args.manga2pdf}'))
        elif args.c:
            convert_manga(args.spath, args.manga2pdf, args.dpath, args.c)
        else:
            parser.error('please specify chapters to convert using arguments: [a, c]')
    elif args.folder2pdf:
        convert_folder(args.spath, args.dpath, args.n)
    else:
        parser.error('at least one argument is required')