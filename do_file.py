import requests, natsort, time, json, sys, os
from termcolor import colored
from assets import *

global mangas

def download_file(json_file, sleep_time, auto_merge, convert_to_pdf):
    global mangas
    with open(json_file) as mangas_json:
        mangas = json.loads(mangas_json.read())
    get_name_of_chapters(json_file, sleep_time)
    download_mangas(json_file, sleep_time, auto_merge, convert_to_pdf)

def get_name_of_chapters(json_file, sleep_time):
    global mangas
    valid_mangas = [manga for (manga, detm) in mangas.items() if detm['include']]
    for valid_manga in valid_mangas:
        manga = mangas[valid_manga]
        sys.stdout.write(f'\r{valid_manga}: Getting name of chapters...')
        if manga['last_downloaded_chapter'] != 'pass':
            chapters = sources_dict[manga['domain']].get_chapters(manga['url'])
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
        manga['chapters'] = sorted(manga['chapters'], key=lambda _: (sources_dict[manga['domain']].rename_chapter, natsort.os_sorted))
        print(f'\r{valid_manga}: There are totally {len(manga["chapters"])} chapters to download.')
        time.sleep(sleep_time)
    with open(json_file, 'w') as mangas_json:
        mangas_json.write(json.dumps(mangas, indent=4))

def download_mangas(json_file, sleep_time, auto_merge, convert_to_pdf):
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
                        response = send_request(images[i])
                        with open(save_path, 'wb') as image:
                            image.write(response.content)
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
                with open(json_file, 'w') as mangas_json:
                    mangas_json.write(json.dumps(mangas, indent=4))
            except Exception as error:
                if str(error) == 'Connection error':
                    waiter()
                if str(error) == 'truncated':
                    print(colored(f' {last_truncated} was truncated. trying to download it one more time...', 'red'))
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
    parser.add_argument('-t', action='store', default=0.1, nargs=1, type=float, help='set sleep time between requests')
    
    args = parser.parse_args()
    args.t = args.t[0] if type(args.t) is list else args.t
    os.system('color')
    download_file(args.f, args.t, args.g, args.p)