from utils.logger import log_over, log
from utils.assets import save_dict_to_file, sleep
from utils.exceptions import MissingFunctionException

def search_wrapper(keyword, modules, absolute, limit_page):
    results = {}
    for module in modules:
        try:
            temp_results, page = search(keyword, module, absolute, limit_page)
            log(f'\r{module.domain}: {len(temp_results)} results were found from {page} pages.', 'green' if temp_results else 'yellow')
            if temp_results:
                results[module.domain] = temp_results
        except MissingFunctionException as error:
            log(error, 'red')
    save_dict_to_file(f'{keyword}_output.json', results)
    print_output(results)
    log(f'This was a summary of the search.\nYou can see the full results in {keyword}_output.json', 'green')

def search(keyword, module, absolute, limit_page):
    results = {}
    if not hasattr(module, 'search_by_keyword'):
        raise MissingFunctionException(module.domain, 'search_by_keyword')
    search = module.search_by_keyword(keyword, absolute)
    page = 1
    while page <= limit_page:
        try:
            log_over(f'\r{module.domain}: Searching page {page}...')
            last = next(search)
            if not last:
                break
            results.update(last)
            page += 1
            if page < limit_page:
                sleep()
        except Exception as error:
            log(f'\r{module.domain}: Failed to search: {error}', 'red')
            break
    return results, page-1

def print_output(results):
    log('Summary:')
    for module, data in results.items():
        log(f'{module}:')
        for result, value in list(data.items())[:5]:
            refer = 'url' if 'url' in value else 'code'
            log(f'    title: {result}, {refer}: {value[refer]}')