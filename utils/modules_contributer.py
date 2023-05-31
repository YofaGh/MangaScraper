def get_module(key):
    match key:
        case 'bibimanga.com':
            from modules.Bibimanga import Bibimanga
            return Bibimanga
        case 'blogmanga.net':
            from modules.Blogmanga import Blogmanga
            return Blogmanga
        case 'coloredmanga.com':
            from modules.Coloredmanga import Coloredmanga
            return Coloredmanga
        case 'comics.8muses.com':
            from modules.Comics8Muses import Comics8Muses
            return Comics8Muses
        case 'hentaifox.com':
            from modules.Hentaifox import Hentaifox
            return Hentaifox
        case 'imhentai.xxx':
            from modules.Imhentai import Imhentai
            return Imhentai
        case 'manga18.club':
            from modules.Manga18 import Manga18
            return Manga18
        case 'manga18fx.com':
            from modules.Manga18fx import Manga18fx
            return Manga18fx
        case 'manga18h.com':
            from modules.Manga18h import Manga18h
            return Manga18h
        case 'manga68.com':
            from modules.Manga68 import Manga68
            return Manga68
        case 'mangaforfree.net':
            from modules.Mangaforfree import Mangaforfree
            return Mangaforfree
        case 'mangapark.to':
            from modules.Mangapark import Mangapark
            return Mangapark
        case 'mangareader.cc':
            from modules.Mangareader import Mangareader
            return Mangareader
        case 'manhuamix.com':
            from modules.Manhuamix import Manhuamix
            return Manhuamix
        case 'manhuascan.us':
            from modules.Manhuascan import Manhuascan
            return Manhuascan
        case 'manhwa18.com':
            from modules.Manhwa18 import Manhwa18
            return Manhwa18
        case 'nhentai.xxx':
            from modules.Nhentai import Nhentai
            return Nhentai
        case 'nyahentai.red':
            from modules.Nyahentai import Nyahentai
            return Nyahentai
        case 'readonepiece.com':
            from modules.Readonepiece import Readonepiece
            return Readonepiece
        case 'sarrast.com':
            from modules.Sarrast import Sarrast
            return Sarrast
        case 'simplyhentai.org':
            from modules.Simplyhentai import Simplyhentai
            return Simplyhentai
        case _:
            from utils.exceptions import MissingModuleException
            raise MissingModuleException(key)

def get_all_modules():
    from modules.Bibimanga import Bibimanga
    from modules.Blogmanga import Blogmanga
    from modules.Coloredmanga import Coloredmanga
    from modules.Comics8Muses import Comics8Muses
    from modules.Hentaifox import Hentaifox
    from modules.Imhentai import Imhentai
    from modules.Manga18 import Manga18
    from modules.Manga18fx import Manga18fx
    from modules.Manga18h import Manga18h
    from modules.Manga68 import Manga68
    from modules.Mangaforfree import Mangaforfree
    from modules.Mangapark import Mangapark
    from modules.Mangareader import Mangareader
    from modules.Manhuamix import Manhuamix
    from modules.Manhuascan import Manhuascan
    from modules.Manhwa18 import Manhwa18
    from modules.Nhentai import Nhentai
    from modules.Nyahentai import Nyahentai
    from modules.Readonepiece import Readonepiece
    from modules.Sarrast import Sarrast
    from modules.Simplyhentai import Simplyhentai
    return [
        Bibimanga,
        Blogmanga,
        Coloredmanga,
        Comics8Muses,
        Hentaifox,
        Imhentai,
        Manga18,
        Manga18fx,
        Manga18h,
        Manga68,
        Mangaforfree,
        Mangapark,
        Mangareader,
        Manhuamix,
        Manhuascan,
        Manhwa18,
        Nhentai,
        Nyahentai,
        Readonepiece,
        Sarrast,
        Simplyhentai
    ]

def get_all_domains():
    return [
        'bibimanga.com',
        'blogmanga.net',
        'coloredmanga.com',
        'comics.8muses.com',
        'hentaifox.com',
        'imhentai.xxx',
        'manga18.club',
        'manga18fx.com',
        'manga18h.com',
        'manga68.com',
        'mangaforfree.net',
        'mangapark.to',
        'mangareader.cc',
        'manhuamix.com',
        'manhuascan.us',
        'manhwa18.com',
        'nhentai.xxx',
        'nyahentai.red' ,
        'readonepiece.com',
        'sarrast.com',
        'simplyhentai.org'
    ]