from utils.logger import log
from utils.modules_contributer import get_modules
from utils.exceptions import MissingModuleException
from downloaders.doujin_single import download_doujin
from utils.assets import save_json_file, load_json_file


def download_doujins(json_file: str) -> None:
    doujins = load_json_file(json_file)
    valid_domains = [doujin for (doujin, detm) in doujins.items() if detm]
    for domain in valid_domains:
        try:
            i = 0
            while i < len(doujins[domain]):
                if download_doujin(doujins[domain][i], get_modules(domain)):
                    del doujins[domain][i]
                    save_json_file(json_file, doujins)
                else:
                    i += 1
        except MissingModuleException as error:
            log(error, "red")
