import natsort, time, sys, os
from termcolor import colored
from utils import assets

def download_single(manga, url, source, sleep_time, is_all, last, ranged, chapters, auto_merge, convert_to_pdf):
    chapters_to_download = get_name_of_chapters(manga, url, source, is_all, last, ranged, chapters)
    download_manga(manga, url, source, sleep_time, chapters_to_download, auto_merge, convert_to_pdf)

def get_name_of_chapters(manga, url, source, is_all, last, ranged, c_chapters):
    ctd = []
    sys.stdout.write(f'\r{manga}: Getting name of chapters...')
    chapters = source.get_chapters(url)
    if is_all:
        ctd = chapters.copy()
    if last:
        reached_last_downloaded_chapter = False
        for chapter in chapters:
            if source.rename_chapter(chapter) == source.rename_chapter(str(last)):
                reached_last_downloaded_chapter = True
                continue
            if reached_last_downloaded_chapter:
                ctd.append(chapter)
    if ranged:
        reached_beginning_chapter = False
        for chapter in chapters:
            if source.rename_chapter(chapter) == source.rename_chapter(str(ranged[0])):
                reached_beginning_chapter = True
            if reached_beginning_chapter:
                ctd.append(chapter)
            if source.rename_chapter(chapter) == source.rename_chapter(str(ranged[1])):
                break
    if c_chapters:
        renamed_chapters = [source.rename_chapter(str(c)) for c in c_chapters]
        ctd += [chapter for chapter in chapters if (source.rename_chapter(chapter) in renamed_chapters and chapter not in ctd)]
    print(f'\r{manga}: There are totally {len(ctd)} chapters to download.')
    return sorted(ctd, key=lambda _: (source.rename_chapter, natsort.os_sorted))

def download_manga(manga, url, source, sleep_time, chapters, auto_merge, convert_to_pdf):
    inconsistencies = []
    last_truncated = None
    fixed_manga = assets.fix_manga_name(manga)
    assets.create_folder(fixed_manga)
    while len(chapters) > 0:
        renamed_chapter = source.rename_chapter(chapters[0])
        sys.stdout.write(f'\r{manga}: Creating folder for {chapters[0]}...')
        assets.create_folder(f'{fixed_manga}/{renamed_chapter}')
        try:
            sys.stdout.write(f'\r{manga}: Getting image links of {chapters[0]}...')
            images, save_names = source.get_images(url, chapters[0])
            adder = 0
            for i in range(len(images)):
                sys.stdout.write(f'\r{manga}: Downloading {chapters[0]} image {i+adder+1}/{len(images)+adder}...')
                if not save_names:
                    if f'{i+adder+1}' not in images[i].split('/')[-1]:
                        adder += 1
                        inconsistencies.append(f'{manga}/{chapters[0]}/{i+adder:03d}')
                        print(colored(f' Warning: Inconsistency in order of images!!!. Skipped image {i + adder}', 'red'))
                        sys.stdout.write(f'\r{manga}: Downloading {chapters[0]} image {i+adder+1}/{len(images)+adder}...')
                    save_path = f'{fixed_manga}/{renamed_chapter}/{i+adder+1:03d}.{images[i].split(".")[-1]}'
                else:
                    save_path = f'{fixed_manga}/{renamed_chapter}/{save_names[i]}'
                if not os.path.exists(save_path):
                    time.sleep(sleep_time)
                    response = source.send_request(images[i])
                    with open(save_path, 'wb') as image:
                        image.write(response.content)
                    if not assets.validate_corrupted_image(save_path):
                        print(colored(f' Warning: Image {i+adder+1} is corrupted. will not be able to merge this chapter', 'red'))
                    if not assets.validate_truncated_image(save_path) and last_truncated != save_path:
                        last_truncated = save_path
                        os.remove(save_path)
                        raise Exception('truncated')
            print(colored(f'\r{manga}: {chapters[0]} is done downloading, {len(images)} images were downloaded.', 'green'))
            if auto_merge:
                from utils.image_merger import merge_chapter
                merge_chapter(manga, renamed_chapter)
            if convert_to_pdf:
                from utils.pdf_converter import convert_chapter
                convert_chapter('Merged', manga, renamed_chapter, f'Merged/{manga}')
            del chapters[0]
        except Exception as error:
            if 'Connection error' in str(error):
                assets.waiter()
            if str(error) == 'truncated':
                print(colored(f' {last_truncated} was truncated. trying to download it one more time...', 'red'))
            else:
                print(error)
    if inconsistencies:
        print(colored(f'There were some inconsistencies in the following chapters: {", ".join(inconsistencies)}', 'red'))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('-u', action='store', required=True, help='url of the manga')
    parser.add_argument('-s', action=assets.SetSource, required=True, help='domain to scrap from')
    parser.add_argument('-c', action=assets.CheckChapters, nargs='+', type=float, help='specifie chapters')
    parser.add_argument('-n', action='store',  help='specifie name of mangas folder')
    parser.add_argument('-p', action='store_true', help='converts merged images to pdf')
    parser.add_argument('-g', action='store_true', help='if set, merges images vertically')
    parser.add_argument('-t', action='store', default=0.1, nargs=1, type=float, help='set sleep time between requests')
    
    single_manga_chapters = parser.add_mutually_exclusive_group()
    single_manga_chapters.add_argument('-a', action='store_true', help='downloads all available chapters')
    single_manga_chapters.add_argument('-l', action=assets.LastChapter, type=float, help='\
        downloads all available chapters after the given chapter')
    single_manga_chapters.add_argument('-r', action=assets.RangeOfChapters, nargs=2, type=float, help='\
        downloads all available chapters between the given chapters')
    args = parser.parse_args()
    if not (args.c or args.a or args.l or args.r):
        parser.error('specify chapters using arguments: [a, l, r, c]')
    args.t = args.t[0] if type(args.t) is list else args.t
    os.system('color')
    download_single(args.n or args.u, args.s, args.u, args.a, args.l, args.r, args.c, args.g, args.p)