import natsort, sys
from termcolor import colored
from utils.modules_contributer import get_module
from utils.exceptions import MissingModuleException
from utils.assets import save_dict_to_file, load_dict_from_file

def download_file(json_file, sleep_time, merge, convert_to_pdf, resize):
    get_name_of_chapters(json_file)
    inconsistencies = download_mangas(json_file, sleep_time, merge, convert_to_pdf, resize)
    if inconsistencies:
        print(colored(f'There were some inconsistencies with the following chapters: {", ".join(inconsistencies)}', 'red'))

def get_name_of_chapters(json_file):
    mangas = load_dict_from_file(json_file)
    valid_mangas = [manga for (manga, detm) in mangas.items() if detm['include']]
    for valid_manga in valid_mangas:
        manga = mangas[valid_manga]
        sys.stdout.write(f'\r{valid_manga}: Getting chapters...')
        if manga['last_downloaded_chapter'] != 'pass':
            chapters = get_module(manga['domain']).get_chapters(manga['url'])
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
        manga['chapters'] = sorted(manga['chapters'], key=lambda _: (get_module(manga['domain']).rename_chapter, natsort.os_sorted))
        print(f'\r{valid_manga}: {len(manga["chapters"])} chapter{"" if len(manga["chapters"]) == 1 else "s"} to download.')
    save_dict_to_file(json_file, mangas)

def download_mangas(json_file, sleep_time, merge, convert_to_pdf, resize):
    from downloaders.manga_single import download_manga
    mangas = load_dict_from_file(json_file)
    inconsistencies = []
    valid_mangas = [manga for (manga, detm) in mangas.items() if (detm['include'] and detm['chapters'])]
    for manga in valid_mangas:
        try:
            while len(mangas[manga]['chapters']) > 0:
                chapter = mangas[manga]['chapters'][0]
                module = get_module(mangas[manga]['domain'])
                ics = download_manga(manga, mangas[manga]['url'], module, sleep_time, [chapter], merge, convert_to_pdf, resize)
                inconsistencies += ics
                if module.rename_chapter(chapter) > module.rename_chapter(mangas[manga]['last_downloaded_chapter']):
                    mangas[manga]['last_downloaded_chapter'] = chapter
                del mangas[manga]['chapters'][0]
                save_dict_to_file(json_file, mangas)
        except MissingModuleException as error:
            print(colored(error, 'red'))
    return inconsistencies