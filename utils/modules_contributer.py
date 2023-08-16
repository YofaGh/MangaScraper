def get_module(key):
    match key:
        case 'allmanga.to':
            from modules.Allmanga import Allmanga
            return Allmanga
        case 'bato.to':
            from modules.Bato import Bato
            return Bato
        case 'bibimanga.com':
            from modules.Bibimanga import Bibimanga
            return Bibimanga
        case 'blogmanga.net':
            from modules.Blogmanga import Blogmanga
            return Blogmanga
        case 'coloredmanga.com':
            from modules.Coloredmanga import Coloredmanga
            return Coloredmanga
        case 'comick.app':
            from modules.Comick import Comick
            return Comick
        case 'comics.8muses.com':
            from modules.Comics8Muses import Comics8Muses
            return Comics8Muses
        case 'constellarcomic.com':
            from modules.Constellarcomic import Constellarcomic
            return Constellarcomic
        case 'doujins.com':
            from modules.Doujins import Doujins
            return Doujins
        case 'ehentai.to':
            from modules.Ehentai import Ehentai
            return Ehentai
        case 'hennojin.com':
            from modules.Hennojin import Hennojin
            return Hennojin
        case 'hentaifox.com':
            from modules.Hentaifox import Hentaifox
            return Hentaifox
        case 'hentaixcomic.com':
            from modules.Hentaixcomic import Hentaixcomic
            return Hentaixcomic
        case 'imhentai.xxx':
            from modules.Imhentai import Imhentai
            return Imhentai
        case 'luscious.net':
            from modules.Luscious import Luscious
            return Luscious
        case 'manga18.club':
            from modules.Manga18 import Manga18
            return Manga18
        case 'manga18fx.com':
            from modules.Manga18fx import Manga18fx
            return Manga18fx
        case 'manga18h.com':
            from modules.Manga18h import Manga18h
            return Manga18h
        case 'manga18hot.net':
            from modules.Manga18hot import Manga18hot
            return Manga18hot
        case 'manga68.com':
            from modules.Manga68 import Manga68
            return Manga68
        case 'mangadex.org':
            from modules.Mangadex import Mangadex
            return Mangadex
        case 'mangadistrict.com':
            from modules.Mangadistrict import Mangadistrict
            return Mangadistrict
        case 'mangaforfree.net':
            from modules.Mangaforfree import Mangaforfree
            return Mangaforfree
        case 'mangahentai.me':
            from modules.Mangahentai import Mangahentai
            return Mangahentai
        case 'mangapark.to':
            from modules.Mangapark import Mangapark
            return Mangapark
        case 'mangareader.mobi':
            from modules.Mangareader import Mangareader
            return Mangareader
        case 'manhuamanhwa.com':
            from modules.Manhuamanhwa import Manhuamanhwa
            return Manhuamanhwa
        case 'manhuamix.com':
            from modules.Manhuamix import Manhuamix
            return Manhuamix
        case 'manhuascan.us':
            from modules.Manhuascan import Manhuascan
            return Manhuascan
        case 'manhwa18.com':
            from modules.Manhwa18 import Manhwa18
            return Manhwa18
        case 'manytoon.com':
            from modules.Manytoon import Manytoon
            return Manytoon
        case 'myreadingmanga.to':
            from modules.Myreadingmanga import Myreadingmanga
            return Myreadingmanga
        case 'myrockmanga.com':
            from modules.Myrockmanga import Myrockmanga
            return Myrockmanga
        case 'nhentai.xxx':
            from modules.Nhentai import Nhentai
            return Nhentai
        case 'nyahentai.red':
            from modules.Nyahentai import Nyahentai
            return Nyahentai
        case 'omegascans.org':
            from modules.Omegascans import Omegascans
            return Omegascans
        case 'readonepiece.com':
            from modules.Readonepiece import Readonepiece
            return Readonepiece
        case 'sarrast.com':
            from modules.Sarrast import Sarrast
            return Sarrast
        case 'simply-hentai.com':
            from modules.Simply_hentai import Simply_hentai
            return Simply_hentai
        case 'simplyhentai.org':
            from modules.Simplyhentai import Simplyhentai
            return Simplyhentai
        case 'toonily.com':
            from modules.Toonily import Toonily_Com
            return Toonily_Com
        case 'toonily.me':
            from modules.Toonily import Toonily_Me
            return Toonily_Me
        case 'truemanga.com':
            from modules.Truemanga import Truemanga
            return Truemanga
        case 'vyvymanga.net':
            from modules.Vyvymanga import Vyvymanga
            return Vyvymanga
        case 'w.mangairo.com':
            from modules.WMangairo import WMangairo
            return WMangairo
        case _:
            from utils.exceptions import MissingModuleException
            raise MissingModuleException(key)

def get_all_modules():
    from modules.Allmanga import Allmanga
    from modules.Bato import Bato
    from modules.Bibimanga import Bibimanga
    from modules.Blogmanga import Blogmanga
    from modules.Coloredmanga import Coloredmanga
    from modules.Comics8Muses import Comics8Muses
    from modules.Comick import Comick
    from modules.Constellarcomic import Constellarcomic
    from modules.Doujins import Doujins
    from modules.Ehentai import Ehentai
    from modules.Hennojin import Hennojin
    from modules.Hentaifox import Hentaifox
    from modules.Hentaixcomic import Hentaixcomic
    from modules.Imhentai import Imhentai
    from modules.Luscious import Luscious
    from modules.Manga18 import Manga18
    from modules.Manga18fx import Manga18fx
    from modules.Manga18h import Manga18h
    from modules.Manga18hot import Manga18hot
    from modules.Manga68 import Manga68
    from modules.Mangadex import Mangadex
    from modules.Mangadistrict import Mangadistrict
    from modules.Mangaforfree import Mangaforfree
    from modules.Mangahentai import Mangahentai
    from modules.Mangapark import Mangapark
    from modules.Mangareader import Mangareader
    from modules.Manhuamanhwa import Manhuamanhwa
    from modules.Manhuamix import Manhuamix
    from modules.Manhuascan import Manhuascan
    from modules.Manhwa18 import Manhwa18
    from modules.Manytoon import Manytoon
    from modules.Myreadingmanga import Myreadingmanga
    from modules.Myrockmanga import Myrockmanga
    from modules.Nhentai import Nhentai
    from modules.Nyahentai import Nyahentai
    from modules.Omegascans import Omegascans
    from modules.Readonepiece import Readonepiece
    from modules.Sarrast import Sarrast
    from modules.Simply_hentai import Simply_hentai
    from modules.Simplyhentai import Simplyhentai
    from modules.Toonily import Toonily_Com
    from modules.Toonily import Toonily_Me
    from modules.Truemanga import Truemanga
    from modules.Vyvymanga import Vyvymanga
    from modules.WMangairo import WMangairo
    return [
        Allmanga,
        Bato,
        Bibimanga,
        Blogmanga,
        Coloredmanga,
        Comick,
        Comics8Muses,
        Constellarcomic,
        Doujins,
        Ehentai,
        Hennojin,
        Hentaifox,
        Hentaixcomic,
        Imhentai,
        Luscious,
        Manga18,
        Manga18fx,
        Manga18h,
        Manga18hot,
        Manga68,
        Mangadex,
        Mangadistrict,
        Mangaforfree,
        Mangahentai,
        Mangapark,
        Mangareader,
        Manhuamanhwa,
        Manhuamix,
        Manhuascan,
        Manhwa18,
        Manytoon,
        Myreadingmanga,
        Myrockmanga,
        Nhentai,
        Nyahentai,
        Omegascans,
        Readonepiece,
        Sarrast,
        Simply_hentai,
        Simplyhentai,
        Toonily_Com,
        Toonily_Me,
        Truemanga,
        Vyvymanga,
        WMangairo
    ]

def get_all_domains():
    return [
        'allmanga.to',
        'bato.to',
        'bibimanga.com',
        'blogmanga.net',
        'coloredmanga.com',
        'comick.com',
        'comics.8muses.com',
        'constellar.com',
        'doujins.com',
        'ehentai.to',
        'hennojin.com',
        'hentaifox.com',
        'hentaixcomic.com',
        'imhentai.xxx',
        'luscious.net',
        'manga18.club',
        'manga18fx.com',
        'manga18h.com',
        'manga18hot.net',
        'manga68.com',
        'mangadex.com',
        'mangadistrict.com',
        'mangaforfree.net',
        'mangahentai.me',
        'mangapark.to',
        'mangareader.mobi',
        'manhuamanhwa.com',
        'manhuamix.com',
        'manhuascan.us',
        'manhwa18.com',
        'manytoon.com',
        'myreadingmanga.to',
        'myrockmanga.com',
        'nhentai.xxx',
        'nyahentai.red',
        'omegascans.org',
        'readonepiece.com',
        'sarrast.com',
        'simply-hentai.com',
        'simplyhentai.org',
        'toonily.com',
        'toonily.me',
        'truemanga.com',
        'vyvymanga.net',
        'w.mangairo.com'
    ]