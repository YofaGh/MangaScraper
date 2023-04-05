import natsort, json, sys
from utils.modules_contributer import get_class
from termcolor import colored

def download_file(json_file, sleep_time, merge, convert_to_pdf):
    get_name_of_chapters(json_file)
    inconsistencies = download_mangas(json_file, sleep_time, merge, convert_to_pdf)
    if inconsistencies:
        print(colored(f'There were some inconsistencies with the following chapters: {", ".join(inconsistencies)}', 'red'))

def get_name_of_chapters(json_file):
    with open(json_file) as mangas_json:
        mangas = json.loads(mangas_json.read())
    valid_mangas = [manga for (manga, detm) in mangas.items() if detm['include']]
    for valid_manga in valid_mangas:
        manga = mangas[valid_manga]
        sys.stdout.write(f'\r{valid_manga}: Getting name of chapters...')
        if manga['last_downloaded_chapter'] != 'pass':
            chapters = get_class(manga['domain']).get_chapters(manga['url'])
            if manga['last_downloaded_chapter'] is None:
                manga['chapters'] += [chapter for chapter in chapters if chapter not in manga['chapters']]
            else:
                reached_last_downloaded_chapter = False
                for chapter in chapters:
                    if chapter == manga['last_downloaded_chapter']:
                        reached_last_downloaded_chapter = True
                        continue
                    if reached_last_downloaded_chapter and chapter not in manga['chapters']:
                        manga['chapters'].append(chapter)
        manga['chapters'] = sorted(manga['chapters'], key=lambda _: (get_class(manga['domain']).rename_chapter, natsort.os_sorted))
        print(f'\r{valid_manga}: There are totally {len(manga["chapters"])} chapters to download.')
    with open(json_file, 'w') as mangas_json:
        mangas_json.write(json.dumps(mangas, indent=4))

def download_mangas(json_file, sleep_time, merge, convert_to_pdf):
    with open(json_file) as mangas_json:
        mangas = json.loads(mangas_json.read())
    inconsistencies = []
    valid_mangas = [manga for (manga, detm) in mangas.items() if (detm['include'] and detm['chapters'])]
    for manga in valid_mangas:
        while len(mangas[manga]['chapters']) > 0:
            try:
                chapter = mangas[manga]['chapters'][0]
                source = get_class(mangas[manga]['domain'])
                from downloaders.manga_single import download_manga
                ics = download_manga(manga, mangas[manga]['url'], source, sleep_time, [chapter], merge, convert_to_pdf)
                inconsistencies += ics
                if source.rename_chapter(chapter) > source.rename_chapter(mangas[manga]['last_downloaded_chapter']):
                    mangas[manga]['last_downloaded_chapter'] = chapter
                del mangas[manga]['chapters'][0]
                with open(json_file, 'w') as mangas_json:
                    mangas_json.write(json.dumps(mangas, indent=4))
            except Exception as error:
                print(error)
    return inconsistencies