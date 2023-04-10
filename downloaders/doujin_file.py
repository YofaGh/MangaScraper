from termcolor import colored
from utils.modules_contributer import get_class
from utils.exceptions import MissingModuleException
from downloaders.doujin_single import download_doujin
from utils.assets import save_dict_to_file, load_dict_from_file

def download_doujins(json_file, sleep_time, merge, convert_to_pdf):
    doujins = load_dict_from_file(json_file)
    valid_doujins = [doujin for (doujin, detm) in doujins.items() if detm['codes']]
    for doujin in valid_doujins:
        try:
            source = get_class(doujin)
            while len(doujins[doujin]['codes']) > 0:
                code = doujins[doujin]['codes'][0]
                download_doujin(code, source, sleep_time, merge, convert_to_pdf)
                del doujins[doujin]['codes'][0]
                save_dict_to_file(save_dict_to_file, doujins)
        except MissingModuleException as error:
            print(colored(error, 'red'))