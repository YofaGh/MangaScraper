import time, sys
from utils.modules_contributer import contributer

def search_by_title(title, sources):
    results = {}
    for source in sources:
        search = contributer(source).search_by_title(title)
        while True:
            try:
                last = next(search)
                if type(last) == int:
                    sys.stdout.write(f'\r{source}: searching page {last}...')
                    last_page = last
                time.sleep(2)
            except:
                print(f'\r{source}: {len(last)} results were found from {last_page-1} pages.')
                results[source] = last
                break
    return results