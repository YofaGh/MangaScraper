import time, os
from contextlib import suppress
from utils.logger import log_over, log
from utils.exceptions import MissingFunctionException
from utils.assets import validate_corrupted_image, validate_truncated_image, load_dict_from_file

def check_modules(modules):
    samples = load_dict_from_file('test_samples.json')
    for module in modules:
        if module.type == 'Manga':
            check_manga(module, samples[module.domain])
        elif module.type == 'Doujin':
            check_doujin(module, samples[module.domain])

def check_manga(module, sample):
    chapters = chapter_checker(module, sample['manga'])
    if chapters:
        images, save_names = manga_images_checker(module, sample['manga'], chapters[0])
    else:
        images = []
        log(f'\r{module.domain}: {sample["manga"]}: Skipped images_checker due to chapter_checker failure', 'red')
    if images:
        if save_names:
            download_checker(module, images[0], save_names[0])
        else:
            download_checker(module, images[0], f'{module.domain}_test.{images[0].split(".")[-1]}')
    else:
        log(f'\r{module.domain}: {sample["manga"]}: Skipped download_checker due to images_checker failure', 'red')
    search_by_keyword_checker(module, sample.get('keyword', 'a'))
    get_db_checker(module)

def check_doujin(module, sample):
    title_checker(module, sample['doujin'])
    images, save_names = doujin_images_checker(module, sample['doujin'])
    if images:
        if save_names:
            download_checker(module, images[0], save_names[0])
        else:
            download_checker(module, images[0], f'{module.domain}_test.{images[0].split(".")[-1]}')
    else:
        log(f'\r{module.domain}: {sample["doujin"]}: Skipped download_checker due to images_checker failure', 'red')
    search_by_keyword_checker(module, sample.get('keyword', 'a'))
    get_db_checker(module)

def chapter_checker(module, manga):
    chapters = []
    log_over(f'\r{module.domain}: {manga}: Getting chapters...')
    with suppress(Exception): chapters = module.get_chapters(manga)
    if chapters:
        log(f'\r{module.domain}: {manga}: Recieved chapters successfully', 'green')
    else:
        log(f'\r{module.domain}: {manga}: Recieving chapters was a failure', 'red')
    return chapters

def title_checker(module, code):
    log_over(f'\r{module.domain}: {code}: Getting title...')
    try:
        module.get_title(code)
        log(f'\r{module.domain}: {code}: Recieved title successfully', 'green')
    except:
        log(f'\r{module.domain}: {code}: Recieving title was a failure', 'red')

def manga_images_checker(module, manga, chapter):
    images, save_names = [], []
    log_over(f'\r{module.domain}: {manga}: {chapter["name"]}: Getting images...')
    with suppress(Exception): images, save_names = module.get_images(manga, chapter)
    if images:
        log(f'\r{module.domain}: {manga}: {chapter["name"]}: Recieved images links successfully', 'green')
    else:
        log(f'\r{module.domain}: {manga}: {chapter["name"]}: Recieving images links was a failure', 'red')
    return images, save_names

def doujin_images_checker(module, code):
    images, save_names = [], []
    log_over(f'\r{module.domain}: {code}: Getting images...')
    with suppress(Exception): images, save_names = module.get_images(code)
    if images:
        log(f'\r{module.domain}: {code}: Recieved images links successfully', 'green')
    else:
        log(f'\r{module.domain}: {code}: Recieving images links was a failure', 'red')
    return images, save_names

def download_checker(module, url, name):
    log_over(f'\r{module.domain}: Running download checker...')
    try:
        saved_path = module.download_image(url, name, f'{module.domain}_test')
        if validate_corrupted_image(saved_path) and validate_truncated_image(saved_path):
            os.remove(saved_path)
            log(f'\r{module.domain}: Downloaded an image successfully', 'green')
        else:
            raise Exception
    except:
        log(f'\r{module.domain}: Downloading image was a failure', 'red')

def search_by_keyword_checker(module, keyword):
    log_over(f'\r{module.domain}: Checkeing search function...')
    try:
        if not hasattr(module, 'search_by_keyword'):
            raise MissingFunctionException(module.domain, 'search_by_keyword')
        search = module.search_by_keyword(keyword, False)
        page = 1
        results = {}
        while page <= 2:
            try:
                last = next(search)
                if len(last) == 0:
                    break
                results.update(last)
                page += 1
                if page < 2:
                    time.sleep(0.1)
            except Exception as error:
                break
        if len(results) > 0:
            log(f'\r{module.domain}: Searched in module successfully', 'green')
        else:
            raise Exception('Empty results')
    except Exception as error:
        log(f'\r{module.domain}: Searching by keyword was a failure: {error}', 'red')

def get_db_checker(module):
    log_over(f'\r{module.domain}: Checkeing get_db function...')
    try:
        if not hasattr(module, 'get_db'):
            raise MissingFunctionException(module.domain, 'get_db')
        results = {}
        crawler = module.get_db()
        page = 1
        while page <= 2:
            try:
                last = next(crawler)
                if len(last) == 0:
                    break
                results.update(last)
                page += 1
                if page < 2:
                    time.sleep(0.1)
            except Exception as error:
                break
        if len(results) > 0:
            log(f'\r{module.domain}: Crawled database successfully', 'green')
        else:
            raise Exception('Empty results')
    except Exception as error:
        log(f'\r{module.domain}: Crawling database was a failure: {error}', 'red')