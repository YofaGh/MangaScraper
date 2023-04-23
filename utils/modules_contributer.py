from modules.Bibimanga import Bibimanga
from modules.Blogmanga import Blogmanga
from modules.Coloredmanga import Coloredmanga
from modules.Comics8Muses import Comics8Muses
from modules.Hentaifox import Hentaifox
from modules.Imhentai import Imhentai
from modules.Manga18fx import Manga18fx
from modules.Manga18h import Manga18h
from modules.Mangaforfree import Mangaforfree
from modules.Mangapark import Mangapark
from modules.Mangareader import Mangareader
from modules.Manhuamanhwa import Manhuamanhwa
from modules.Manhuamix import Manhuamix
from modules.Manhuascan import Manhuascan
from modules.Manhwa18 import Manhwa18
from modules.Nhentai import Nhentai
from modules.Nyahentai import Nyahentai
from modules.Readonepiece import Readonepiece
from modules.Sarrast import Sarrast
from modules.Simplyhentai import Simplyhentai
from modules.Truemanga import Truemanga

sources_dict = {
    'bibimanga.com': Bibimanga,
    'blogmanga.net': Blogmanga,
    'coloredmanga.com': Coloredmanga,
    'comics.8muses.com': Comics8Muses,
    'hentaifox.com': Hentaifox,
    'imhentai.xxx': Imhentai,
    'manga18fx.com': Manga18fx,
    'manga18h.com': Manga18h,
    'mangaforfree.net': Mangaforfree,
    'mangapark.to': Mangapark,
    'mangareader.cc': Mangareader,
    'manhuamanhwa.com': Manhuamanhwa,
    'manhuamix.com': Manhuamix,
    'manhuascan.us': Manhuascan,
    'manhwa18.com': Manhwa18,
    'nhentai.xxx': Nhentai,
    'nyahentai.red': Nyahentai,
    'readonepiece.com': Readonepiece,
    'sarrast.com': Sarrast,
    'simplyhentai.org': Simplyhentai,
    'truemanga.com': Truemanga
}

def get_all_domains():
    return list(sources_dict.keys())

def get_all_modules():
    return list(sources_dict.values())

def get_module(key):
    try:
        return sources_dict[key]
    except:
        from utils.exceptions import MissingModuleException
        raise MissingModuleException(key)