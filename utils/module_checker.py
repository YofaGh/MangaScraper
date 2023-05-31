import time, sys, os
from termcolor import colored
from contextlib import suppress
from utils.models import Manga, Doujin
from utils.exceptions import MissingFunctionException
from utils.assets import validate_corrupted_image, validate_truncated_image, load_dict_from_file

def check_modules(sources):
    samples = load_dict_from_file('test_samples.json')
    for source in sources:
        if Manga in source.__bases__:
            check_manga(source, samples[source.domain])
        elif Doujin in source.__bases__:
            check_doujin(source, samples[source.domain])

def check_manga(source, sample):
    chapters = chapter_checker(source, sample['manga'])
    if len(chapters) > 0:
        images, save_names = manga_images_checker(source, sample['manga'], chapters[0])
    else:
        images = []
        print(colored(f'\r{source.domain}: {sample["manga"]}: Skipped images_checker due to chapter_checker failure', 'red'))
    if len(images) > 0:
        if save_names:
            download_checker(source, images[0], save_names[0])
        else:
            download_checker(source, images[0], f'{source.domain}_test.{images[0].split(".")[-1]}')
    else:
        print(colored(f'\r{source.domain}: {sample["manga"]}: Skipped download_checker due to images_checker failure', 'red'))
    search_by_keyword_checker(source, sample['keyword'])
    get_db_checker(source)

def check_doujin(source, sample):
    title_checker(source, sample['doujin'])
    images = doujin_images_checker(source, sample['doujin'])
    if len(images) > 0:
        download_checker(source, images[0], f'{source.domain}_test.{images[0].split(".")[-1]}')
    else:
        print(colored(f'\r{source.domain}: {sample["doujin"]}: Skipped download_checker due to images_checker failure', 'red'))
    search_by_keyword_checker(source, sample['keyword'])
    get_db_checker(source)

def chapter_checker(source, manga):
    chapters = []
    sys.stdout.write(f'\r{source.domain}: {manga}: Getting chapters...')
    with suppress(Exception): chapters = source.get_chapters(manga)
    if len(chapters) > 0:
        print(colored(f'\r{source.domain}: {manga}: Recieved chapters successfully', 'green'))
    else:
        print(colored(f'\r{source.domain}: {manga}: Recieving chapters was a failure', 'red'))
    return chapters

def title_checker(source, code):
    sys.stdout.write(f'\r{source.domain}: {code}: Getting title...')
    try:
        source.get_title(code)
        print(colored(f'\r{source.domain}: {code}: Recieved title successfully', 'green'))
    except:
        print(colored(f'\r{source.domain}: {code}: Recieving title was a failure', 'red'))

def manga_images_checker(source, manga, chapter):
    images, save_names = [], []
    sys.stdout.write(f'\r{source.domain}: {manga}: {chapter}: Getting images...')
    with suppress(Exception): images, save_names = source.get_images(manga, chapter)
    if len(images) > 0:
        print(colored(f'\r{source.domain}: {manga}: {chapter}: Recieved images links successfully', 'green'))
    else:
        print(colored(f'\r{source.domain}: {manga}: {chapter}: Recieving images links was a failure', 'red'))
    return images, save_names

def doujin_images_checker(source, code):
    images = []
    sys.stdout.write(f'\r{source.domain}: {code}: Getting images...')
    with suppress(Exception): images = source.get_images(code)
    if len(images) > 0:
        print(colored(f'\r{source.domain}: {code}: Recieved images links successfully', 'green'))
    else:
        print(colored(f'\r{source.domain}: {code}: Recieving images links was a failure', 'red'))
    return images

def download_checker(source, url, name):
    sys.stdout.write(f'\r{source.domain}: Running download checker...')
    try:
        saved_path = source.download_image(url, name, f'{source.domain}_test')
        if validate_corrupted_image(saved_path) and validate_truncated_image(saved_path):
            os.remove(saved_path)
            print(colored(f'\r{source.domain}: Downloaded an image successfully', 'green'))
        else:
            raise Exception
    except:
        print(colored(f'\r{source.domain}: Downloading image was a failure', 'red'))

def search_by_keyword_checker(source, keyword):
    sys.stdout.write(f'\r{source.domain}: Checkeing search function...')
    try:
        if not hasattr(source, 'search_by_keyword'):
            raise MissingFunctionException(source.domain, 'search_by_keyword')
        search = source.search_by_keyword(keyword, False)
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
            print(colored(f'\r{source.domain}: Searched in module successfully', 'green'))
        else:
            print(colored(f'\r{source.domain}: Searching by keyword was a failue: empty results', 'red'))
    except Exception as error:
        print(colored(f'\r{source.domain}: Searching by keyword was a failure: {error}', 'red'))

def get_db_checker(source):
    sys.stdout.write(f'\r{source.domain}: Checkeing get_db function...')
    try:
        if not hasattr(source, 'get_db'):
            raise MissingFunctionException(source.domain, 'get_db')
        results = {}
        crawler = source.get_db()
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
            print(colored(f'\r{source.domain}: Crawled database successfully', 'green'))
        else:
            print(colored(f'\r{source.domain}: Crawling database was a failue: empty results', 'red'))
    except Exception as error:
        print(colored(f'\r{source.domain}: Crawling database was a failure: {error}', 'red'))