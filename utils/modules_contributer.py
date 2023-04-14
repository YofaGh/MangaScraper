from modules.Bibimanga import Bibimanga
from modules.Blogmanga import Blogmanga
from modules.Coloredmanga import Coloredmanga
from modules.Comics8Muses import Comics8Muses
from modules.Hentaifox import Hentaifox
from modules.Manga18fx import Manga18fx
from modules.Manga18h import Manga18h
from modules.Mangapark import Mangapark
from modules.Mangareader import Mangareader
from modules.Manhuamanhwa import Manhuamanhwa
from modules.Manhuascan import Manhuascan
from modules.Manhwa18 import Manhwa18
from modules.Nhentai import Nhentai
from modules.Nyahentai import Nyahentai
from modules.Readonepiece import Readonepiece
from modules.Simplyhentai import Simplyhentai
from modules.Truemanga import Truemanga

sources_dict = {
    'bibimanga.com': Bibimanga,
    'blogmanga.net': Blogmanga,
    'coloredmanga.com': Coloredmanga,
    'comics.8muses.com': Comics8Muses,
    'hentaifox.com': Hentaifox,
    'manga18fx.com': Manga18fx,
    'manga18h.com': Manga18h,
    'mangapark.to': Mangapark,
    'mangareader.cc': Mangareader,
    'manhuamanhwa.com': Manhuamanhwa,
    'manhuascan.us': Manhuascan,
    'manhwa18.com': Manhwa18,
    'nhentai.xxx': Nhentai,
    'nyahentai.red': Nyahentai,
    'readonepiece.com': Readonepiece,
    'simplyhentai.org': Simplyhentai,
    'truemanga.com': Truemanga
}

def get_all_domains():
    return list(sources_dict.keys())

def get_all_classes():
    return list(sources_dict.values())

def get_domain(value):
    for domain, source in sources_dict.items():
        if source == value:
            return domain
    else:
        from utils.exceptions import UnknownModuleException
        raise UnknownModuleException(value)

def get_class(key):
    try:
        return sources_dict[key]
    except:
        from utils.exceptions import MissingModuleException
        raise MissingModuleException(key)