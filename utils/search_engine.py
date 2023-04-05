import time, sys
from utils.modules_contributer import get_domain

def search_by_title(title, sources, absolute=False, limit_page=1000, save_to_file=False):
    results = {}
    for source in sources:
        try:
            if not hasattr(source, 'search_by_title'):
                raise Exception('searching by title is not yet implemented for this domain.')
            domain = get_domain(source)
            search = source.search_by_title(title, absolute=absolute, limit_page=limit_page)
            while True:
                is_done, last = next(search)
                if not is_done:
                    sys.stdout.write(f'\r{domain}: Searching page {last}...')
                    last_page = last
                    time.sleep(2)
                else:
                    print(f'\r{domain}: {len(last)} results were found from {last_page-1} pages.')
                    results[domain] = last
                    break
        except Exception as error:
            sys.stdout.write(f'\r{domain}: Failed to search: {error}\n')
    print_output(results)
    if save_to_file:
        save_results(results)

def print_output(results):
    for source in results:
        print(f'{source}:')
        for result in results[source]:
            print(f'    title: {results[source][result]}, url: {result}')

def save_results(results):
    import json
    with open('output.json', 'w') as output:
        output.write(json.dumps(results, indent=4))