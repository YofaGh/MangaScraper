from utils.logger import log
from utils.modules_contributer import get_module
from utils.exceptions import MissingModuleException
from downloaders.doujin_single import download_doujin
from utils.assets import save_dict_to_file, load_dict_from_file

def download_doujins(json_file):
    doujins = load_dict_from_file(json_file)
    valid_doujins = [doujin for (doujin, detm) in doujins.items() if detm['codes']]
    for doujin in valid_doujins:
        try:
            i = 0
            while len(doujins[doujin]['codes']) - i > 0:
                if download_doujin(doujins[doujin]['codes'][i], get_module(doujin)):
                    del doujins[doujin]['codes'][i]
                else:
                    i += 1
                save_dict_to_file(json_file, doujins)
        except MissingModuleException as error:
            log(error, 'red')