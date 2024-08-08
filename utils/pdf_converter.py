import img2pdf
from utils.logger import log_over, log
from utils.assets import validate_folder, create_folder

def convert_folder(path_to_source: str, path_to_destination: str, pdf_name: str, name: str | None = None) -> None:
    name = name or path_to_source
    pdf_name = pdf_name if pdf_name.endswith('.pdf') else f'{pdf_name}.pdf'
    invalid_image, images_path = validate_folder(path_to_source)
    if invalid_image:
        log(f'\rFailed to convert {path_to_source} because this image is invalid: {invalid_image}', 'red')
        return
    if not images_path:
        log(f'\rFailed to convert {path_to_source} because there was no image in the given folder.', 'red')
        return
    create_folder(path_to_destination)
    log_over(f'\r{name}: Converting to pdf...')
    with open(f'{path_to_destination}/{pdf_name}', 'wb') as pdf_file:
        pdf_file.write(img2pdf.convert(images_path))
    log(f'\r{name}: Converted to pdf.      ', 'green')

def convert_bulk(path_to_source: str, path_to_destination: str) -> None:
    import os
    sub_folders = os.listdir(path_to_source)
    for sub_folder in sub_folders:
        convert_folder(f'{path_to_source}/{sub_folder}', path_to_destination, f'{path_to_source}_{sub_folder}', f'{path_to_source}: {sub_folder}')

def convert_bulkone(path_to_source: str, path_to_destination: str) -> None:
    import os
    sub_folders = os.listdir(path_to_source)
    images = []
    log_over(f'\r{path_to_source}: Detecting images...')
    for sub_folder in sub_folders:
        invalid_image, images_path = validate_folder(f'{path_to_source}/{sub_folder}')
        if invalid_image:
            log(f'\rFailed to convert {path_to_source}/{sub_folder} because this image is invalid: {invalid_image}', 'red')
            return
        images += images_path
    if not images:
        log(f'\rFailed to convert {path_to_source} because there was no image in the given folder.', 'red')
        return
    log_over(f'\r{path_to_source}: Creating pdf...    ')
    with open(f'{path_to_destination}/{path_to_source}.pdf', 'wb') as pdf_file:
        pdf_file.write(img2pdf.convert(images))
    log(f'\r{path_to_source}: Converted all subfolders to one pdf.      ', 'green')