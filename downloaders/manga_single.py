import time, sys, os
from termcolor import colored
from utils import assets, exceptions
from requests.exceptions import HTTPError, Timeout

def download_single(manga, url, module, sleep_time, last, ranged, chapters, merge, convert_to_pdf, fit_merge):
    chapters_to_download = get_name_of_chapters(manga, url, module, last, ranged, chapters)
    inconsistencies = download_manga(manga, url, module, sleep_time, chapters_to_download, merge, convert_to_pdf, fit_merge)
    if inconsistencies:
        print(colored(f'There were some inconsistencies with the following chapters: {", ".join(inconsistencies)}', 'red'))

def get_name_of_chapters(manga, url, module, last, ranged, c_chapters):
    ctd = []
    sys.stdout.write(f'\r{manga}: Getting chapters...')
    chapters = module.get_chapters(url)
    if last:
        reached_last_downloaded_chapter = False
        last_downloaded_chapter = module.rename_chapter(str(last))
        for chapter in chapters:
            if module.rename_chapter(chapter) == last_downloaded_chapter:
                reached_last_downloaded_chapter = True
                continue
            if reached_last_downloaded_chapter:
                ctd.append(chapter)
    elif ranged:
        reached_beginning_chapter = False
        beginning_chapter = module.rename_chapter(str(ranged[0]))
        ending_chapter = module.rename_chapter(str(ranged[1]))
        for chapter in chapters:
            renamed_chapter = module.rename_chapter(chapter)
            if renamed_chapter == beginning_chapter:
                reached_beginning_chapter = True
            if reached_beginning_chapter:
                ctd.append(chapter)
            if renamed_chapter == ending_chapter:
                break
    elif c_chapters:
        renamed_chapters = [module.rename_chapter(str(c)) for c in c_chapters]
        ctd = [chapter for chapter in chapters if (module.rename_chapter(chapter) in renamed_chapters)]
    else:
        ctd = chapters
    print(f'\r{manga}: {len(ctd)} chapter{"" if len(ctd) == 1 else "s"} to download.')
    return ctd

def download_manga(manga, url, module, sleep_time, chapters, merge, convert_to_pdf, fit_merge):
    inconsistencies = []
    last_truncated = None
    fixed_manga = assets.fix_name_for_folder(manga)
    assets.create_folder(fixed_manga)
    while len(chapters) > 0:
        chapter = chapters[0]
        renamed_chapter = module.rename_chapter(chapter)
        try:
            sys.stdout.write(f'\r{manga}: {chapter}: Getting image links...')
            images, save_names = module.get_images(url, chapter)
            sys.stdout.write(f'\r{manga}: {chapter}: Creating folder...')
            path = f'{fixed_manga}/{renamed_chapter}'
            assets.create_folder(f'{fixed_manga}/{renamed_chapter}')
            adder = 0
            i = 0
            while i < len(images):
                sys.stdout.write(f'\r{manga}: {chapter}: Downloading image {i+adder+1}/{len(images)+adder}...')
                if save_names:
                    save_path = f'{path}/{save_names[i]}'
                else:
                    if f'{i+adder+1}' not in images[i].split('/')[-1]:
                        adder += 1
                        inconsistencies.append(f'{manga}/{chapter}/{i+adder:03d}.{images[i].split(".")[-1]}')
                        print(colored(f' Warning: Inconsistency in order of images!!!. Skipped image {i + adder}', 'red'))
                        sys.stdout.write(f'\r{manga}: {chapter}: Downloading image {i+adder+1}/{len(images)+adder}...')
                    save_path = f'{path}/{i+adder+1:03d}.{images[i].split(".")[-1]}'
                if not os.path.exists(save_path):
                    time.sleep(sleep_time)
                    saved_path = module.download_image(images[i], save_path, i+adder+1, module.download_images_headers)
                    if not assets.validate_corrupted_image(saved_path):
                        print(colored(f' Warning: Image {i+adder+1} is corrupted. will not be able to merge this chapter', 'red'))
                        i += 1
                        continue
                    if not assets.validate_truncated_image(saved_path) and last_truncated != saved_path:
                        last_truncated = saved_path
                        os.remove(saved_path)
                        print(colored(f' Warning: Image {i+adder+1} was truncated. trying to download it one more time...', 'red'))
                        i -= 1
                i += 1
            print(colored(f'\r{manga}: {chapter}: Finished downloading, {len(images)} images were downloaded.', 'green'))
            del chapters[0]
            if merge:
                from utils.image_merger import merge_folder
                merge_folder(path, f'Merged/{path}', fit_merge, f'{manga}: {chapter}')
            if convert_to_pdf:
                from utils.pdf_converter import convert_folder
                convert_folder(path, fixed_manga, f'{manga}_{renamed_chapter}', f'{manga}: {chapter}')
        except (Timeout, HTTPError, exceptions.ImageMergerException, exceptions.PDFConverterException) as error:
            print(colored(error, 'red'))
    return inconsistencies