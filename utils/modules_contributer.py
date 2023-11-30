modules = {
    'allmanga.to': 'Allmanga',
    'bato.to': 'Bato',
    'bibimanga.com': 'Bibimanga',
    'coloredmanga.com': 'Coloredmanga',
    'comick.app': 'Comick',
    'comics.8muses.com': 'Comics8Muses',
    'constellarcomic.com': 'Constellarcomic',
    'doujins.com': 'Doujins',
    'ehentai.to': 'Ehentai',
    'hennojin.com': 'Hennojin',
    'hentaifox.com': 'Hentaifox',
    'hentaixcomic.com': 'Hentaixcomic',
    'imhentai.xxx': 'Imhentai',
    'luscious.net': 'Luscious',
    'manga18.club': 'Manga18',
    'manga18fx.com': 'Manga18fx',
    'manga18h.com': 'Manga18h',
    'manga18hot.net': 'Manga18hot',
    'manga68.com': 'Manga68',
    'mangadex.org': 'Mangadex',
    'mangadistrict.com': 'Mangadistrict',
    'mangaforfree.net': 'Mangaforfree',
    'mangahentai.me': 'Mangahentai',
    'mangapark.to': 'Mangapark',
    'mangareader.mobi': 'Mangareader',
    'manhuamanhwa.com': 'Manhuamanhwa',
    'manhuamix.com': 'Manhuamix',
    'manhuascan.us': 'Manhuascan',
    'manhwa18.com': 'Manhwa18',
    'manytoon.com': 'Manytoon',
    'myreadingmanga.to': 'Myreadingmanga',
    'myrockmanga.com': 'Myrockmanga',
    'nhentai.com': 'Nhentai_Com',
    'nhentai.xxx': 'Nhentai_Xxx',
    '9hentai.to': 'NineHentai',
    'nyahentai.red': 'Nyahentai',
    'omegascans.org': 'Omegascans',
    'readonepiece.com': 'Readonepiece',
    'sarrast.com': 'Sarrast',
    'simply-hentai.com': 'Simply_hentai',
    'simplyhentai.org': 'Simplyhentai',
    'toonily.com': 'Toonily_Com',
    'toonily.me': 'Toonily_Me',
    'truemanga.com': 'Truemanga',
    'vyvymanga.net': 'Vyvymanga',
    'w.mangairo.com': 'WMangairo'
}

def import_module(module_name):
    return getattr(__import__(f'modules.{module_name}', fromlist=[module_name]), module_name)

def get_modules(key=None):
    if not key:
        return [import_module(module) for module in modules.values()]
    if isinstance(key, list):
        return [get_modules(module) for module in key]
    if key in modules:
        return import_module(modules[key])
    from utils.exceptions import MissingModuleException
    raise MissingModuleException(key)