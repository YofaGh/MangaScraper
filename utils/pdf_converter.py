import img2pdf, sys, os
from utils import assets
from termcolor import colored

def convert_folder(path_to_source, path_to_destination, pdf_name, name=None):
    name = name if name else path_to_source
    if not assets.validate_folder(path_to_source):
        print(colored(f'\rFailed to convert {path_to_source} because of a corrupted image.', 'red'))
        return
    assets.create_path(path_to_destination)
    sys.stdout.write(f'\r{name}: Converting to pdf...')
    images_path = assets.detect_images(path_to_source)
    with open(os.path.join(path_to_destination, pdf_name), 'wb') as pdf_file:
        pdf_file.write(img2pdf.convert(images_path))
    print(colored(f'\r{name}: Converted to pdf.      ', 'green'))

def convert_bulk(path_to_source, path_to_destination):
    sub_folders = os.listdir(path_to_source)
    for sub_folder in sub_folders:
        convert_folder(f'{path_to_source}/{sub_folder}', path_to_destination, f'{path_to_source}_{sub_folder}.pdf', f'{path_to_source}: {sub_folder}')