import textwrap, os
from requests.exceptions import HTTPError, Timeout
from utils.models import Doujin
from utils.logger import log, log_over
from settings import AUTO_MERGE, AUTO_PDF_CONVERSION
from utils.exceptions import ImageMergerException, PDFConverterException
from utils.assets import fix_name_for_folder, create_folder, validate_corrupted_image, validate_truncated_image, sleep

def download_doujin(code: str, module: Doujin) -> bool:
    last_truncated = None
    try:
        log_over(f'\r{code}: Getting name of doujin...')
        doujin_title = f'{code}_{module.get_title(code)}' if module.is_coded else module.get_title(code)
        shorten_doujin_title = textwrap.shorten(doujin_title, width=50)
        log_over(f'\r{shorten_doujin_title}: Getting image links...')
        images, save_names = module.get_images(code)
        log_over(f'\r{shorten_doujin_title}: Creating folder...')
        fixed_doujin_name = fix_name_for_folder(doujin_title)
        create_folder(doujin_title)
        i = 0
        while i < len(images):
            log_over(f'\r{shorten_doujin_title}: Downloading image {i+1}/{len(images)}...')
            if save_names:
                save_path = f'{fixed_doujin_name}/{save_names[i]}'
            else:
                save_path = f'{fixed_doujin_name}/{i+1:03d}.{images[i].split(".")[-1]}'
            if not os.path.exists(save_path):
                sleep()
                saved_path = module.download_image(images[i], save_path)
                if not saved_path:
                    log(f' Warning: Image {i+1} could not be downloaded. url: {images[i]}', 'red')
                elif not validate_corrupted_image(saved_path):
                    log(f' Warning: Image {i+1} was corrupted. may not be able to merge this chapter.', 'red')
                elif not validate_truncated_image(saved_path) and last_truncated != saved_path:
                    last_truncated = saved_path
                    os.remove(saved_path)
                    log(f' Warning: Image {i+1} was truncated. trying to download it one more time...', 'red')
                    continue
            i += 1
        log(f'\r{shorten_doujin_title}: Finished downloading, {len(images)} images were downloaded.', 'green')
        if AUTO_MERGE:
            from utils.image_merger import merge_folder
            merge_folder(fixed_doujin_name, f'Merged/{fixed_doujin_name}', shorten_doujin_title)
        if AUTO_PDF_CONVERSION:
            from utils.pdf_converter import convert_folder
            convert_folder(fixed_doujin_name, fixed_doujin_name, fixed_doujin_name, shorten_doujin_title)
        return True
    except (Timeout, HTTPError, ImageMergerException, PDFConverterException) as error:
        log(error, 'red')
        return False