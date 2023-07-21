import textwrap, time, sys, os
from termcolor import colored
from utils import assets, exceptions
from requests.exceptions import HTTPError, Timeout

def download_doujin(code, module, sleep_time, merge, convert_to_pdf, fit_merge):
    last_truncated = None
    try:
        sys.stdout.write(f'\r{code}: Getting name of doujin...')
        doujin_title = f'{code}_{module.get_title(code)}'
        shorten_doujin_title = textwrap.shorten(doujin_title, width=50)
        sys.stdout.write(f'\r{shorten_doujin_title}: Getting image links...')
        images = module.get_images(code)
        sys.stdout.write(f'\r{shorten_doujin_title}: Creating folder...')
        fixed_doujin_name = assets.fix_name_for_folder(doujin_title)
        assets.create_folder(fixed_doujin_name)
        i = 0
        while i < len(images):
            sys.stdout.write(f'\r{shorten_doujin_title}: Downloading image {i+1}/{len(images)}...')
            save_path = f'{fixed_doujin_name}/{i+1:03d}.{images[i].split(".")[-1]}'
            if not os.path.exists(save_path):
                time.sleep(sleep_time)
                saved_path = module.download_image(images[i], save_path, i+1, module.download_images_headers)
                if not assets.validate_corrupted_image(saved_path):
                    print(colored(f' Warning: Image {i+1} is corrupted. will not be able to merge this chapter.', 'red'))
                    i += 1
                    continue
                if not assets.validate_truncated_image(saved_path) and last_truncated != saved_path:
                    last_truncated = saved_path
                    os.remove(saved_path)
                    print(colored(f' Warning: Image {i+1} was truncated. trying to download it one more time...', 'red'))
                    i -= 1
            i += 1
        print(colored(f'\r{shorten_doujin_title}: Finished downloading, {len(images)} images were downloaded.', 'green'))
        if merge:
            from utils.image_merger import merge_folder
            merge_folder(fixed_doujin_name, f'Merged/{fixed_doujin_name}', fit_merge, shorten_doujin_title)
        if convert_to_pdf:
            from utils.pdf_converter import convert_folder
            convert_folder(fixed_doujin_name, fixed_doujin_name, fixed_doujin_name, shorten_doujin_title)
        return True
    except (Timeout, HTTPError, exceptions.ImageMergerException, exceptions.PDFConverterException) as error:
        print(colored(error, 'red'))
        return False