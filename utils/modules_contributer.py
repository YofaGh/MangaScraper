from modules.Bibimanga import Bibimanga
from modules.Hentaifox import Hentaifox
from modules.Mangapark import Mangapark
from modules.Mangareader import Mangareader
from modules.Manhuascan import Manhuascan
from modules.Manhwa18 import Manhwa18
from modules.Manhwa365 import Manhwa365
from modules.Nhentai import Nhentai
from modules.Nyahentai import Nyahentai
from modules.Readonepiece import Readonepiece
from modules.Skymanga import Skymanga
from modules.Truemanga import Truemanga

sources_dict = {
    'bibimanga.com': Bibimanga,
    'hentaifox.com': Hentaifox,
    'mangapark.to': Mangapark,
    'mangareader.cc': Mangareader,
    'manhuascan.us': Manhuascan,
    'manhwa18.com': Manhwa18,
    'manhwa365.com': Manhwa365,
    'nhentai.xxx': Nhentai,
    'nyahentai.red': Nyahentai,
    'readonepiece.com': Readonepiece,
    'skymanga.xyz': Skymanga,
    'truemanga.com': Truemanga
}

def contributer(key):
    return sources_dict[key]