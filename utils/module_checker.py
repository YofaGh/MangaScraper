import time, sys, os
from termcolor import colored
from contextlib import suppress
from utils.models import Manga, Doujin
from utils.exceptions import MissingFunctionException
from utils.assets import validate_corrupted_image, validate_truncated_image, load_dict_from_file

def check_modules(modules):
    samples = load_dict_from_file('test_samples.json')
    for module in modules:
        if Manga in module.__bases__:
            check_manga(module, samples[module.domain])
        elif Doujin in module.__bases__:
            check_doujin(module, samples[module.domain])

def check_manga(module, sample):
    chapters = chapter_checker(module, sample['manga'])
    if len(chapters) > 0:
        images, save_names = manga_images_checker(module, sample['manga'], chapters[0])
    else:
        images = []
        print(colored(f'\r{module.domain}: {sample["manga"]}: Skipped images_checker due to chapter_checker failure', 'red'))
    if len(images) > 0:
        if save_names:
            download_checker(module, images[0], save_names[0])
        else:
            download_checker(module, images[0], f'{module.domain}_test.{images[0].split(".")[-1]}')
    else:
        print(colored(f'\r{module.domain}: {sample["manga"]}: Skipped download_checker due to images_checker failure', 'red'))
    search_by_keyword_checker(module, sample['keyword'])
    get_db_checker(module)

def check_doujin(module, sample):
    title_checker(module, sample['doujin'])
    images = doujin_images_checker(module, sample['doujin'])
    if len(images) > 0:
        download_checker(module, images[0], f'{module.domain}_test.{images[0].split(".")[-1]}')
    else:
        print(colored(f'\r{module.domain}: {sample["doujin"]}: Skipped download_checker due to images_checker failure', 'red'))
    search_by_keyword_checker(module, sample['keyword'])
    get_db_checker(module)

def chapter_checker(module, manga):
    chapters = []
    sys.stdout.write(f'\r{module.domain}: {manga}: Getting chapters...')
    with suppress(Exception): chapters = module.get_chapters(manga)
    if len(chapters) > 0:
        print(colored(f'\r{module.domain}: {manga}: Recieved chapters successfully', 'green'))
    else:
        print(colored(f'\r{module.domain}: {manga}: Recieving chapters was a failure', 'red'))
    return chapters

def title_checker(module, code):
    sys.stdout.write(f'\r{module.domain}: {code}: Getting title...')
    try:
        module.get_title(code)
        print(colored(f'\r{module.domain}: {code}: Recieved title successfully', 'green'))
    except:
        print(colored(f'\r{module.domain}: {code}: Recieving title was a failure', 'red'))

def manga_images_checker(module, manga, chapter):
    images, save_names = [], []
    sys.stdout.write(f'\r{module.domain}: {manga}: {chapter}: Getting images...')
    with suppress(Exception): images, save_names = module.get_images(manga, chapter)
    if len(images) > 0:
        print(colored(f'\r{module.domain}: {manga}: {chapter}: Recieved images links successfully', 'green'))
    else:
        print(colored(f'\r{module.domain}: {manga}: {chapter}: Recieving images links was a failure', 'red'))
    return images, save_names

def doujin_images_checker(module, code):
    images = []
    sys.stdout.write(f'\r{module.domain}: {code}: Getting images...')
    with suppress(Exception): images = module.get_images(code)
    if len(images) > 0:
        print(colored(f'\r{module.domain}: {code}: Recieved images links successfully', 'green'))
    else:
        print(colored(f'\r{module.domain}: {code}: Recieving images links was a failure', 'red'))
    return images

def download_checker(module, url, name):
    sys.stdout.write(f'\r{module.domain}: Running download checker...')
    try:
        saved_path = module.download_image(url, name, f'{module.domain}_test', module.download_images_headers)
        if validate_corrupted_image(saved_path) and validate_truncated_image(saved_path):
            os.remove(saved_path)
            print(colored(f'\r{module.domain}: Downloaded an image successfully', 'green'))
        else:
            raise Exception
    except:
        print(colored(f'\r{module.domain}: Downloading image was a failure', 'red'))

def search_by_keyword_checker(module, keyword):
    sys.stdout.write(f'\r{module.domain}: Checkeing search function...')
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
            print(colored(f'\r{module.domain}: Searched in module successfully', 'green'))
        else:
            print(colored(f'\r{module.domain}: Searching by keyword was a failue: empty results', 'red'))
    except Exception as error:
        print(colored(f'\r{module.domain}: Searching by keyword was a failure: {error}', 'red'))

def get_db_checker(module):
    sys.stdout.write(f'\r{module.domain}: Checkeing get_db function...')
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
            print(colored(f'\r{module.domain}: Crawled database successfully', 'green'))
        else:
            print(colored(f'\r{module.domain}: Crawling database was a failue: empty results', 'red'))
    except Exception as error:
        print(colored(f'\r{module.domain}: Crawling database was a failure: {error}', 'red'))