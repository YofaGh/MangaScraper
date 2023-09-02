import textwrap, time, os
from utils import assets, exceptions, logger
from requests.exceptions import HTTPError, Timeout

def download_doujin(code, module, sleep_time, merge, convert_to_pdf, fit_merge):
    last_truncated = None
    try:
        logger.log_over(f'\r{code}: Getting name of doujin...')
        pre_code = f'{code}_' if module.is_coded else ''
        doujin_title = f'{pre_code}{module.get_title(code)}'
        shorten_doujin_title = textwrap.shorten(doujin_title, width=50)
        logger.log_over(f'\r{shorten_doujin_title}: Getting image links...')
        images, save_names = module.get_images(code)
        logger.log_over(f'\r{shorten_doujin_title}: Creating folder...')
        fixed_doujin_name = assets.fix_name_for_folder(doujin_title)
        assets.create_folder(fixed_doujin_name)
        i = 0
        while i < len(images):
            logger.log_over(f'\r{shorten_doujin_title}: Downloading image {i+1}/{len(images)}...')
            if save_names:
                save_path = f'{fixed_doujin_name}/{save_names[i]}'
            else:
                save_path = f'{fixed_doujin_name}/{i+1:03d}.{images[i].split(".")[-1]}'
            if not os.path.exists(save_path):
                time.sleep(sleep_time)
                saved_path = module.download_image(images[i], save_path, i+1)
                if not assets.validate_corrupted_image(saved_path):
                    logger.log(f' Warning: Image {i+1} is corrupted. will not be able to merge this chapter.', 'red')
                    i += 1
                    continue
                if not assets.validate_truncated_image(saved_path) and last_truncated != saved_path:
                    last_truncated = saved_path
                    os.remove(saved_path)
                    logger.log(f' Warning: Image {i+1} was truncated. trying to download it one more time...', 'red')
                    i -= 1
            i += 1
        logger.log(f'\r{shorten_doujin_title}: Finished downloading, {len(images)} images were downloaded.', 'green')
        if merge:
            from utils.image_merger import merge_folder
            merge_folder(fixed_doujin_name, f'Merged/{fixed_doujin_name}', fit_merge, shorten_doujin_title)
        if convert_to_pdf:
            from utils.pdf_converter import convert_folder
            convert_folder(fixed_doujin_name, fixed_doujin_name, fixed_doujin_name, shorten_doujin_title)
        return True
    except (Timeout, HTTPError, exceptions.ImageMergerException, exceptions.PDFConverterException) as error:
        logger.log(error, 'red')
        return False