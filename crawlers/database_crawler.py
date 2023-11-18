from utils.logger import log_over, log
from utils.assets import save_dict_to_file, sleep
from utils.exceptions import MissingFunctionException

def crawl(module):
    try:
        if not hasattr(module, 'get_db'):
            raise MissingFunctionException(module.domain, 'get_db')
        results = {}
        crawler = module.get_db()
        page = 1
        while True:
            try:
                log_over(f'\r{module.domain}: Crawling page {page}...')
                last = next(crawler)
                if not last:
                    break
                results.update(last)
                page += 1
                sleep()
            except Exception as error:
                log(f'\r{module.domain}: Failed to crawl: {error}', 'red')
                break
        log(f'\r{module.domain}: {len(results)} results were crawled from {page-1} pages.', 'green' if len(results) > 0 else 'yellow')
        save_dict_to_file(f'{module.domain}_database.json', results)
        log(f'\r{module.domain}: Results were saved to {module.domain}_database.json', 'green')
    except MissingFunctionException as error:
        log(error, 'red')