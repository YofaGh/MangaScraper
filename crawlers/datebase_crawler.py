import time, sys
from termcolor import colored
from utils.assets import save_dict_to_file
from utils.exceptions import MissingFunctionException

def crawl(source, sleep_time):
    try:
        if not hasattr(source, 'get_db'):
            raise MissingFunctionException(source.domain, 'get_db')
        results = {}
        search = source.get_db()
        page = 1
        while True:
            try:
                sys.stdout.write(f'\r{source.domain}: Crawling page {page}...')
                last = next(search)
                if len(last) == 0:
                    break
                results.update(last)
                page += 1
                time.sleep(sleep_time)
            except Exception as error:
                print(colored(f'\r{source.domain}: Failed to crawl: {error}', 'red'))
                break
        print(colored(f'\r{source.domain}: {len(results)} results were crawled from {page-1} pages.', 'green' if len(results) > 0 else 'yellow'))
        save_dict_to_file(f'{source.domain}_database.json', results)
        print(colored(f'\r{source.domain}: Results were saved to {source.domain}_database.json', 'green'))
    except MissingFunctionException as error:
        print(colored(error, 'red'))