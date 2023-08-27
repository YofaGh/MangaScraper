import time
from utils.logger import log_over, log
from utils.assets import save_dict_to_file
from utils.exceptions import MissingFunctionException

def search(keyword, modules, sleep_time, absolute, limit_page):
    results = {}
    for module in modules:
        try:
            if not hasattr(module, 'search_by_keyword'):
                raise MissingFunctionException(module.domain, 'search_by_keyword')
            search = module.search_by_keyword(keyword, absolute)
            page = 1
            temp_results = {}
            while page <= limit_page:
                try:
                    log_over(f'\r{module.domain}: Searching page {page}...')
                    last = next(search)
                    if not last:
                        break
                    temp_results.update(last)
                    page += 1
                    if page < limit_page:
                        time.sleep(sleep_time)
                except Exception as error:
                    log(f'\r{module.domain}: Failed to search: {error}', 'red')
                    break
            log(f'\r{module.domain}: {len(temp_results)} results were found from {page-1} pages.', 'green' if temp_results else 'yellow')
            if temp_results:
                results[module.domain] = temp_results
        except MissingFunctionException as error:
            log(error, 'red')
    save_dict_to_file(f'{keyword}_output.json', results)
    print_output(results)
    log(f'This was a summary of the search.\nYou can see the full results in {keyword}_output.json', 'green')

def print_output(results):
    log('Summary:')
    for module, data in results.items():
        log(f'{module}:')
        for result, value in list(data.items())[:5]:
            refer = 'url' if 'url' in value else 'code'
            log(f'    title: {result}, {refer}: {value[refer]}')