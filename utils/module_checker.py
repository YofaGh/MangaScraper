import os
from contextlib import suppress
from utils.models import Manga, Doujin
from utils.logger import log_over, log
from utils.modules_contributer import get_modules
from utils.exceptions import MissingFunctionException
from utils.assets import validate_corrupted_image, validate_truncated_image, load_modules_yaml_file, sleep

def check_modules(domains: list[str] | None = None) -> None:
    modules = load_modules_yaml_file()
    domains = domains or modules.keys()
    for domain in domains:
        module = get_modules(domain)
        if modules[domain]['type'] == 'Manga':
            check_manga(module, modules[domain]['test_sample'])
        elif modules[domain]['type'] == 'Doujin':
            check_doujin(module, modules[domain]['test_sample'])
        se_db_checker(module, 'search_by_keyword', modules[domain]['test_sample'].get('keyword', 'a'), False)
        se_db_checker(module, 'get_db')

def check_manga(module: Manga, sample: dict) -> None:
    chapters, images = chapter_checker(module, sample['url']), []
    if chapters:
        images, save_names = get_images_checker(module, f'{sample["url"]}: {chapters[0]["name"]}', sample['url'], chapters[0])
    else:
        log(f'\r{module.domain}: {sample["url"]}: Skipped images_checker due to chapter_checker failure', 'red')
    if images:
        download_checker(module, images[0], save_names[0] if save_names else f'{module.domain}_test.{images[0].split(".")[-1]}')
    else:
        log(f'\r{module.domain}: {sample["url"]}: Skipped download_checker due to images_checker failure', 'red')

def check_doujin(module: Doujin, sample: dict) -> None:
    title_checker(module, sample['url'])
    images, save_names = get_images_checker(module, sample['url'], sample['url'])
    if images:
        download_checker(module, images[0], save_names[0] if save_names else f'{module.domain}_test.{images[0].split(".")[-1]}')
    else:
        log(f'\r{module.domain}: {sample["url"]}: Skipped download_checker due to images_checker failure', 'red')

def chapter_checker(module: Manga, manga: str) -> list[dict]:
    chapters = []
    log_over(f'\r{module.domain}: {manga}: Getting chapters...')
    with suppress(Exception):
        chapters = module.get_chapters(manga)
    if chapters:
        log(f'\r{module.domain}: {manga}: Recieved chapters successfully', 'green')
    else:
        log(f'\r{module.domain}: {manga}: Recieving chapters was a failure', 'red')
    return chapters

def title_checker(module: Doujin, code: str) -> None:
    log_over(f'\r{module.domain}: {code}: Getting title...')
    try:
        module.get_title(code)
        log(f'\r{module.domain}: {code}: Recieved title successfully', 'green')
    except Exception:
        log(f'\r{module.domain}: {code}: Recieving title was a failure', 'red')

def get_images_checker(module: Manga | Doujin, info: str, *args) -> tuple[list[str], list[str] | bool]:
    images, save_names = [], []
    log_over(f'\r{module.domain}: {info}: Getting images...')
    with suppress(Exception):
        images, save_names = module.get_images(*args)
    if images:
        log(f'\r{module.domain}: {info}: Recieved images links successfully', 'green')
    else:
        log(f'\r{module.domain}: {info}: Recieving images links was a failure', 'red')
    return images, save_names

def download_checker(module: Manga | Doujin, url: str, name: str) -> None:
    log_over(f'\r{module.domain}: Running download checker...')
    try:
        saved_path = module.download_image(url, name)
        if validate_corrupted_image(saved_path) and validate_truncated_image(saved_path):
            os.remove(saved_path)
            log(f'\r{module.domain}: Downloaded an image successfully', 'green')
        else:
            raise Exception
    except Exception:
        log(f'\r{module.domain}: Downloading image was a failure', 'red')

def se_db_checker(module: Manga | Doujin, func_name: str, *args) -> None:
    log_over(f'\r{module.domain}: Checking {func_name} function...')
    try:
        if not hasattr(module, func_name):
            raise MissingFunctionException(module.domain, func_name)
        func = getattr(module, func_name)(*args)
        page = 1
        results = {}
        while page <= 2:
            try:
                last = next(func)
                if not last:
                    break
                results.update(last)
                page += 1
                if page < 2:
                    sleep()
            except Exception:
                break
        if results:
            log(f'\r{module.domain}: {func_name} was successfull     ', 'green')
        else:
            raise Exception('Empty results')
    except Exception as error:
        log(f'\r{module.domain}: {func_name} was a failure: {error}', 'red')