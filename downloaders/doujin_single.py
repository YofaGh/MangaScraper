import textwrap, time, sys, os
from termcolor import colored
from utils import assets

def download_doujin(code, source, sleep_time, auto_merge, convert_to_pdf):
    last_truncated = None
    while True:
        try:
            sys.stdout.write(f'\r{code}: Getting name of doujin...')
            doujin_title = source.get_title(code)
            shorten_doujin_title = textwrap.shorten(doujin_title, width=50)
            sys.stdout.write(f'\r{shorten_doujin_title}: Creating folder...')
            fixed_doujin_name = assets.fix_name_for_folder(doujin_title)
            assets.create_folder(fixed_doujin_name)
            sys.stdout.write(f'\r{shorten_doujin_title}: Getting image links...')
            images = source.get_images(code)
            adder = 0
            for i in range(len(images)):
                sys.stdout.write(f'\r{shorten_doujin_title}: Downloading image {i+adder+1}/{len(images)+adder}...')
                save_path = f'{fixed_doujin_name}/{i+adder+1:03d}.{images[i].split(".")[-1]}'
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
            print(colored(f'\r{shorten_doujin_title}: done downloading, {len(images)} images were downloaded.', 'green'))
            if auto_merge:
                from utils.image_merger import merge_folder
                sys.stdout.write(f'\r{shorten_doujin_title}: Merging...')
                images_path, lists_to_merge = merge_folder(fixed_doujin_name, f'Merged/{fixed_doujin_name}')
                print(colored(f'\r{shorten_doujin_title}: Merged {len(images_path)} images into {len(lists_to_merge)}.', 'green'))
                if convert_to_pdf:
                    from utils.pdf_converter import convert_folder
                    sys.stdout.write(f'\r{shorten_doujin_title}: Converting to pdf...')
                    convert_folder(f'Merged/{fixed_doujin_name}', f'Merged/{fixed_doujin_name}', f'{fixed_doujin_name}.pdf')
                    print(colored(f'\r{shorten_doujin_title}: Converted to pdf.      ', 'green'))
            break
        except Exception as error:
            if 'Connection error' in str(error):
                assets.waiter()
            if str(error) == 'truncated':
                print(colored(f' {last_truncated} was truncated. trying to download it one more time...', 'red'))
            else:
                raise error

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('-c', action='store', required=True, help='code of the doujin')
    parser.add_argument('-s', action=assets.SetSource, required=True, help='domain to scrap from')
    parser.add_argument('-p', action='store_true', help='converts merged images to pdf')
    parser.add_argument('-g', action='store_true', help='if set, merges images vertically')
    parser.add_argument('-t', action='store', default=0.1, nargs=1, type=float, help='set sleep time between requests')

    args = parser.parse_args()
    args.t = args.t[0] if type(args.t) is list else args.t
    os.system('color')
    download_doujin(args.c, args.s, args.t, args.g, args.p)