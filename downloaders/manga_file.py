import natsort, time, json, sys, os
from utils.modules_contributer import contributer
from termcolor import colored
from utils import assets

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
            chapters = contributer(manga['domain']).get_chapters(manga['url'])
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
        manga['chapters'] = sorted(manga['chapters'], key=lambda _: (contributer(manga['domain']).rename_chapter, natsort.os_sorted))
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
        fixed_manga = assets.fix_name_for_folder(manga)
        assets.create_folder(fixed_manga)
        while len(mangas[manga]['chapters']) > 0:
            chapter = mangas[manga]['chapters'][0]
            source = contributer(mangas[manga]['domain'])
            renamed_chapter = source.rename_chapter(chapter)
            try:
                sys.stdout.write(f'\r{manga}: {chapter}: Getting image links...')
                images, save_names = source.get_images(mangas[manga]['url'], chapter)
                sys.stdout.write(f'\r{manga}: {chapter}: Creating folder...')
                assets.create_folder(f'{fixed_manga}/{renamed_chapter}')
                adder = 0
                for i in range(len(images)):
                    sys.stdout.write(f'\r{manga}: {chapter}: Downloading image {i+adder+1}/{len(images)+adder}...')
                    if not save_names:
                        if f'{i+adder+1}' not in images[i].split('/')[-1]:
                            adder += 1
                            inconsistencies.append(f'{manga}/{chapter}/{i+adder:03d}')
                            print(colored(f' Warning: Inconsistency in order of images!!!. Skipped image {i + adder}', 'red'))
                            sys.stdout.write(f'\r{manga}: {chapter}: Downloading image {i+adder+1}/{len(images)+adder}...')
                        save_path = f'{fixed_manga}/{renamed_chapter}/{i+adder+1:03d}.{images[i].split(".")[-1]}'
                    else:
                        save_path = f'{fixed_manga}/{renamed_chapter}/{save_names[i]}'
                    if not os.path.exists(save_path):
                        time.sleep(sleep_time)
                        response = source.send_request(images[i])
                        with open(save_path, 'wb') as image:
                            image.write(response.content)
                        if not assets.validate_corrupted_image(save_path):
                            print(colored(f' Warning: Image {i+adder+1} is corrupted. will not be able to merge this chapter', 'red'))
                        if not assets.validate_truncated_image(save_path) and last_truncated != save_path:
                            last_truncated = save_path
                            os.remove(save_path)
                            raise Exception('truncated')
                print(colored(f'\r{manga}: {chapter}: Finished downloading, {len(images)} images were downloaded.', 'green'))
                if source.rename_chapter(chapter) > source.rename_chapter(mangas[manga]['last_downloaded_chapter']):
                    mangas[manga]['last_downloaded_chapter'] = chapter
                if auto_merge:
                    from utils.image_merger import merge_folder
                    merge_folder(f'{manga}/{renamed_chapter}', f'Merged/{manga}/{renamed_chapter}', f'{manga}: {chapter}')
                if convert_to_pdf:
                    from utils.pdf_converter import convert_folder
                    convert_folder(f'{manga}/{renamed_chapter}', manga, f'{manga}_{renamed_chapter}.pdf', f'{manga}: {chapter}')
                del mangas[manga]['chapters'][0]
                with open(json_file, 'w') as mangas_json:
                    mangas_json.write(json.dumps(mangas, indent=4))
            except Exception as error:
                if 'Connection error' in str(error):
                    assets.waiter()
                if str(error) == 'truncated':
                    print(colored(f' {last_truncated} was truncated. trying to download it one more time...', 'red'))
                else:
                    raise error
    if inconsistencies:
        print(colored(f'There were some inconsistencies in the following chapters: {", ".join(inconsistencies)}', 'red'))