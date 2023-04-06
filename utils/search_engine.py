import sys
from utils.modules_contributer import get_domain
from termcolor import colored

def search(title, sources, sleep_time, absolute=False, limit_page=1000, save_to_file=False):
    results = {}
    for source in sources:
        try:
            domain = get_domain(source)
            if not hasattr(source, 'search'):
                raise Exception('search function is not yet implemented for this domain.')
            search = source.search(title, sleep_time, absolute=absolute, limit_page=limit_page)
            while True:
                is_done, last = next(search)
                if not is_done:
                    sys.stdout.write(f'\r{domain}: Searching page {last}...')
                    last_page = last
                else:
                    print(colored(f'\r{domain}: {len(last)} results were found from {last_page} pages.', 'green' if len(last) > 0 else 'yellow'))
                    results[domain] = last
                    break
        except Exception as error:
            sys.stdout.write(colored(f'\r{domain}: Failed to search: {error}\n', 'red'))
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