from utils.logger import log_over, log
from utils.assets import save_json_file, sleep
from utils.exceptions import MissingFunctionException

def search_wrapper(keyword, modules, absolute, limit_page):
    results = {}
    for module in modules:
        try:
            temp_results = search(keyword, module, absolute, limit_page)
            if temp_results:
                results[module.domain] = temp_results
        except MissingFunctionException as error:
            log(error, 'red')
    save_json_file(f'{keyword}_output.json', results)
    print_output(results)
    log(f'This was a summary of the search.\nYou can see the full results in {keyword}_output.json', 'green')

def search(keyword, module, absolute, limit_page):
    if not hasattr(module, 'search_by_keyword'):
        raise MissingFunctionException(module.domain, 'search_by_keyword')
    search = module.search_by_keyword(keyword, absolute)
    results, page = {}, 1
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
    log(f'\r{module.domain}: {len(results)} results were found from {page-1} pages.', 'green' if results else 'yellow')
    return results

def print_output(results):
    log('Summary:')
    for module, data in results.items():
        log(f'{module}:')
        for result, value in list(data.items())[:5]:
            refer = 'url' if 'url' in value else 'code'
            log(f'    title: {result}, {refer}: {value[refer]}')