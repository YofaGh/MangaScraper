from utils.logger import log
from utils.modules_contributer import get_modules
from utils.exceptions import MissingModuleException
from downloaders.doujin_single import download_doujin
from utils.assets import save_dict_to_file, load_dict_from_file

def download_doujins(json_file):
    doujins = load_dict_from_file(json_file)
    valid_domains = [doujin for (doujin, detm) in doujins.items() if detm]
    for domain in valid_domains:
        try:
            i = 0
            while len(doujins[domain]) - i > 0:
                if download_doujin(doujins[domain][i], get_modules(domain)):
                    del doujins[domain][i]
                else:
                    i += 1
                save_dict_to_file(json_file, doujins)
        except MissingModuleException as error:
            log(error, 'red')