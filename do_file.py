import requests, time, json, sys, os
from termcolor import colored
from assets import *

global mangas

def download_file(json_file, auto_merge, convert_to_pdf):
    global mangas
    with open(json_file) as mangas_json:
        mangas = json.loads(mangas_json.read())
    get_name_of_chapters()
    download_mangas(auto_merge, convert_to_pdf)

def get_name_of_chapters():
    global mangas
    valid_mangas = [manga for (manga, detm) in mangas.items() if detm['include']]
    for manga in valid_mangas:
        sys.stdout.write(f'\r{manga}: Getting name of chapters...')
        if mangas[manga]['last_downloaded_chapter'] != 'pass':
            chapters = sources_dict[mangas[manga]['domain']].get_chapters(mangas[manga]['url'])
            if mangas[manga]['last_downloaded_chapter'] is None:
                mangas[manga]['chapters'] += [chapter for chapter in chapters if chapter not in mangas[manga]['chapters']]
            else:
                reached_last_downloaded_chapter = False
                for chapter in chapters:
                    if chapter == mangas[manga]['last_downloaded_chapter']:
                        reached_last_downloaded_chapter = True
                        continue
                    if reached_last_downloaded_chapter and chapter not in mangas[manga]['chapters']:
                        mangas[manga]['chapters'].append(chapter)
        mangas[manga]['chapters'] = sorted(mangas[manga]['chapters'], key=sources_dict[mangas[manga]['domain']].rename_chapter)
        print(f'\r{manga}: There are totally {len(mangas[manga]["chapters"])} chapters to download.')
        time.sleep(sleep_time)
    with open('mangas.json', 'w') as mangas_json:
        mangas_json.write(json.dumps(mangas, indent=4))

def download_mangas(auto_merge, convert_to_pdf):
    global mangas
    inconsistencies = []
    last_truncated = None
    valid_mangas = [manga for (manga, detm) in mangas.items() if (detm['include'] and detm['chapters'])]
    for manga in valid_mangas:
        fixed_manga = fix_manga_name(manga)
        create_folder(fixed_manga)
        while len(mangas[manga]['chapters']) > 0:
            chapter = mangas[manga]['chapters'][0]
            source = sources_dict[mangas[manga]['domain']]
            renamed_chapter = source.rename_chapter(chapter)
            create_folder(f'{fixed_manga}/{renamed_chapter}')
            try:
                sys.stdout.write(f'\r{manga}: Creating folder for {chapter}...')
                images = source.get_images(mangas[manga]['url'], chapter)
                adder = 0
                for i in range(len(images)):
                    sys.stdout.write(f'\r{manga}: Downloading {chapter} image {i+adder+1}/{len(images)+adder}...')
                    if f'{i+adder+1}' not in images[i].split('/')[-1]:
                        adder += 1
                        inconsistencies.append(f'{manga}/{chapter}/{i+adder:03d}')
                        print(colored(f' Warning: Inconsistency in order of images!!!. Skipped image {i + adder}', 'red'))
                        sys.stdout.write(f'\r{manga}: Downloading {chapter} image {i+adder+1}/{len(images)+adder}...')
                    save_path = f'{fixed_manga}/{renamed_chapter}/{i+adder+1:03d}.{images[i].split(".")[-1]}'
                    if not os.path.exists(save_path):
                        time.sleep(sleep_time)
                        response = requests.get(images[i])
                        with open(save_path, 'wb') as image:
                            image.write(response.content)
                        time.sleep(0.1)
                        if not validate_corrupted_image(save_path):
                            print(colored(f' Warning: Image {i+adder+1} is corrupted. will not be able to merge this chapter', 'red'))
                    if not validate_truncated_image(save_path) and last_truncated != save_path:
                        last_truncated = save_path
                        os.remove(save_path)
                        raise Exception('truncated')
                print(colored(f'\r{manga}: {chapter} is done downloading, {len(images)} images were downloaded.', 'green'))
                if source.rename_chapter(chapter) > source.rename_chapter(mangas[manga]['last_downloaded_chapter']):
                    mangas[manga]['last_downloaded_chapter'] = chapter
                if auto_merge:
                    from image_merger import merge_chapter
                    merge_chapter(manga, chapter)
                if convert_to_pdf:
                    from pdf_converter import convert_chapter
                    convert_chapter('Merged', manga, chapter, f'Merged/{manga}')
                del mangas[manga]['chapters'][0]
                with open('mangas.json', 'w') as mangas_json:
                    mangas_json.write(json.dumps(mangas, indent=4))
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, ConnectionResetError):
                waiter()
            except Exception as error:
                if str(error) == 'truncated':
                    print(colored(f' {last_truncated} was truncated. trying to download it one more time...', 'red'))
                    time.sleep(1200)
                else:
                    raise error
    if inconsistencies:
        print(colored(f'There were some inconsistencies in the following chapters: {", ".join(inconsistencies)}', 'red'))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('-f', action='store', required=True, help='downloads chapters specified in given json file')
    parser.add_argument('-p', action='store_true', help='converts merged images to pdf')
    parser.add_argument('-g', action='store_true', help='if set, merges images vertically')
    args = parser.parse_args()
    os.system('color')
    download_file(args.f, args.g, args.p)