import time, sys
from termcolor import colored
from requests.exceptions import Timeout
from utils.assets import save_dict_to_file
from utils.exceptions import MissingFunctionException

def search(keyword, sources, sleep_time, absolute, limit_page):
    results = {}
    for source in sources:
        try:
            domain = source.get_domain()
            if not hasattr(source, 'search_by_keyword'):
                raise MissingFunctionException(domain, 'search_by_keyword')
            search = source.search_by_keyword(keyword, absolute)
            page = 1
            temp_results = {}
            while page <= limit_page:
                try:
                    sys.stdout.write(f'\r{domain}: Searching page {page}...')
                    last = next(search)
                    if len(last) == 0:
                        break
                    temp_results.update(last)
                    page += 1
                    if page < limit_page:
                        time.sleep(sleep_time)
                except Timeout as error:
                    print(colored(error, 'red'))
                    break
                except Exception as error:
                    print(colored(f'\r{domain}: Failed to search: {error}', 'red'))
                    break
            print(colored(f'\r{domain}: {len(temp_results)} results were found from {page-1} pages.', 'green' if len(temp_results) > 0 else 'yellow'))
            results[domain] = temp_results
        except MissingFunctionException as error:
            print(colored(error, 'red'))
    save_dict_to_file(f'{keyword}_output.json', results)
    print_output(results)
    print(colored(f'This was a summary of the search.\nYou can see the full results in {keyword}_output.json', 'green'))

def print_output(results):
    print('Summary:')
    for source in results:
        print(f'{source}:')
        for result, value in results[source].items():
            refer = 'url' if 'url' in value else 'code'
            print(f'    title: {result}, {refer}: {value[refer]}')