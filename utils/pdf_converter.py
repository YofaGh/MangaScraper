import img2pdf, sys
from utils import assets
from termcolor import colored

def convert_folder(path_to_source, path_to_destination, pdf_name, name=None):
    name = name if name else path_to_source
    pdf_name = pdf_name if pdf_name.endswith('.pdf') else f'{pdf_name}.pdf'
    if not assets.validate_folder(path_to_source):
        print(colored(f'\rFailed to convert {path_to_source} because of a corrupted image.', 'red'))
        return
    assets.create_path(path_to_destination)
    sys.stdout.write(f'\r{name}: Converting to pdf...')
    images_path = assets.detect_images(path_to_source)
    with open(f'{path_to_destination}/{pdf_name}', 'wb') as pdf_file:
        pdf_file.write(img2pdf.convert(images_path))
    print(colored(f'\r{name}: Converted to pdf.      ', 'green'))

def convert_bulk(path_to_source, path_to_destination):
    import os
    sub_folders = os.listdir(path_to_source)
    for sub_folder in sub_folders:
        convert_folder(f'{path_to_source}/{sub_folder}', path_to_destination, f'{path_to_source}_{sub_folder}', f'{path_to_source}: {sub_folder}')

def convert_bulkone(path_to_source, path_to_destination):
    import os
    sub_folders = os.listdir(path_to_source)
    images = []
    sys.stdout.write(f'\r{path_to_source}: Detecting images...')
    for sub_folder in sub_folders:
        if not assets.validate_folder(f'{path_to_source}/{sub_folder}'):
            print(colored(f'\rFailed to convert {path_to_source}/{sub_folder} because of a corrupted image.', 'red'))
            return
        images_path = assets.detect_images(f'{path_to_source}/{sub_folder}')
        images += images_path
    sys.stdout.write(f'\r{path_to_source}: Creating pdf...    ')
    with open(f'{path_to_destination}/{path_to_source}.pdf', 'wb') as pdf_file:
        pdf_file.write(img2pdf.convert(images))
    print(colored(f'\r{path_to_source}: Converted all subfolders to one pdf.      ', 'green'))