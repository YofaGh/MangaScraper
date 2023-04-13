import time, sys
from termcolor import colored
from requests.exceptions import Timeout
from utils.assets import save_dict_to_file
from utils.modules_contributer import get_domain
from utils.exceptions import MissingFunctionException

def crawl(source, sleep_time):
    try:
        domain = get_domain(source)
        if not hasattr(source, 'get_db'):
            raise MissingFunctionException(domain, 'get_db')
        results = {}
        search = source.get_db()
        page = 1
        while True:
            try:
                sys.stdout.write(f'\r{domain}: Crawling page {page}...')
                last = next(search)
                if len(last) == 0:
                    break
                results.update(last)
                page += 1
                time.sleep(sleep_time)
            except Timeout as error:
                print(colored(error, 'red'))
                break
            except Exception as error:
                print(colored(f'\r{domain}: Failed to crawl: {error}', 'red'))
                break
        print(colored(f'\r{domain}: {len(results)} results were crawled from {page-1} pages.', 'green' if len(results) > 0 else 'yellow'))
        save_dict_to_file(f'{domain}_database.json', results)
        print(colored(f'\r{domain}: Results were saved to {domain}_database.json', 'green'))
    except MissingFunctionException as error:
        print(colored(error, 'red'))