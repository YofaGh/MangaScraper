import textwrap, time, sys, os
from termcolor import colored
from utils import assets, exceptions
from requests.exceptions import RequestException, HTTPError, Timeout

def download_doujin(code, source, sleep_time, merge, convert_to_pdf):
    last_truncated = None
    while True:
        try:
            sys.stdout.write(f'\r{code}: Getting name of doujin...')
            doujin_title = f'{code}_{source.get_title(code)}'
            shorten_doujin_title = textwrap.shorten(doujin_title, width=50)
            sys.stdout.write(f'\r{shorten_doujin_title}: Getting image links...')
            images = source.get_images(code)
            sys.stdout.write(f'\r{shorten_doujin_title}: Creating folder...')
            fixed_doujin_name = assets.fix_name_for_folder(doujin_title)
            assets.create_folder(fixed_doujin_name)
            for i in range(len(images)):
                sys.stdout.write(f'\r{shorten_doujin_title}: Downloading image {i+1}/{len(images)}...')
                save_path = f'{fixed_doujin_name}/{i+1:03d}.{images[i].split(".")[-1]}'
                if not os.path.exists(save_path):
                    time.sleep(sleep_time)
                    try:
                        source.download_image(images[i], fixed_doujin_name, f'{i+1:03d}.{images[i].split(".")[-1]}')
                    except HTTPError:
                        print(colored(f'Could not download image {i+1}: {images[i]}', 'red'))
                        continue
                    if not assets.validate_corrupted_image(save_path):
                        print(colored(f' Warning: Image {i+1} is corrupted. will not be able to merge this chapter', 'red'))
                        continue
                    if not assets.validate_truncated_image(save_path) and last_truncated != save_path:
                        raise exceptions.TruncatedException(save_path)
            print(colored(f'\r{shorten_doujin_title}: Finished downloading, {len(images)} images were downloaded.', 'green'))
            if merge:
                from utils.image_merger import merge_folder
                merge_folder(fixed_doujin_name, f'Merged/{fixed_doujin_name}', shorten_doujin_title)
            if convert_to_pdf:
                from utils.pdf_converter import convert_folder
                convert_folder(fixed_doujin_name, fixed_doujin_name, fixed_doujin_name, shorten_doujin_title)
            return True
        except (Timeout, HTTPError, exceptions.ImageMergerException, exceptions.PDFConverterException) as error:
            print(colored(error, 'red'))
            return False
        except RequestException:
            assets.waiter()
        except exceptions.TruncatedException as error:
            last_truncated = error.save_path
            os.remove(last_truncated)
            print(colored(error, 'red'))