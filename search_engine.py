import time, sys
from assets import sources_dict
from sources import *

def search_by_title(title):
    results = {}
    sources = ['manhuascan.us', 'skymanga.xyz', 'bibimanga.com', 'manhwa18.com', 'manhwa365.com']
    for source in sources:
        search = sources_dict[source].search_by_title(title)
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

print(search_by_title('secret'))