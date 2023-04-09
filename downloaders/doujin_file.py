import json
from termcolor import colored
from utils.modules_contributer import get_class
from utils.exceptions import MissingModuleException
from downloaders.doujin_single import download_doujin

def download_doujins(json_file, sleep_time, merge, convert_to_pdf):
    with open(json_file) as doujins_json:
        doujins = json.loads(doujins_json.read())
    valid_doujins = [doujin for (doujin, detm) in doujins.items() if detm['codes']]
    for doujin in valid_doujins:
        try:
            source = get_class(doujin)
            while len(doujins[doujin]['codes']) > 0:
                code = doujins[doujin]['codes'][0]
                download_doujin(code, source, sleep_time, merge, convert_to_pdf)
                del doujins[doujin]['codes'][0]
                with open(json_file, 'w') as doujins_json:
                    doujins_json.write(json.dumps(doujins, indent=4))
        except MissingModuleException as error:
            print(colored(error, 'red'))