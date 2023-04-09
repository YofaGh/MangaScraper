import time, sys
from termcolor import colored
from requests.exceptions import Timeout
from utils.modules_contributer import get_domain
from utils.exceptions import MissingFunctionException

def search(title, sources, sleep_time, absolute, limit_page, save_to_file):
    results = {}
    for source in sources:
        try:
            domain = get_domain(source)
            if not hasattr(source, 'search'):
                raise MissingFunctionException(domain, 'search')
            search = source.search(title, absolute)
            page = 1
            results[domain] = []
            while page <= limit_page:
                try:
                    sys.stdout.write(f'\r{domain}: Searching page {page}...')
                    last = next(search)
                    if len(last) == 0:
                        break
                    results[domain] += last
                    page += 1
                    if page < limit_page:
                        time.sleep(sleep_time)
                except Timeout as error:
                    print(colored(error, 'red'))
                    break
                except Exception as error:
                    print(colored(f'\r{domain}: Failed to search: {error}', 'red'))
                    break
            print(colored(f'\r{domain}: {len(results[domain])} results were found from {page-1} pages.', 'green' if len(results[domain]) > 0 else 'yellow'))
        except MissingFunctionException as error:
            print(colored(error, 'red'))
    print_output(results)
    if save_to_file:
        save_results(title, results)

def print_output(results):
    for source in results:
        print(f'{source}:')
        for result in results[source]:
            print(f'    {result}')

def save_results(title, results):
    import json
    with open(f'{title}_output.json', 'w') as output:
        output.write(json.dumps(results, indent=4))