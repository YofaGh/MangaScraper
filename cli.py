import argparse, settings, sys, os

class SetChapters(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if self.dest == 'r' and values[0] > values[1]:
            raise ValueError('The beginning chapter must be lower than the ending chapter')
        if self.dest == 'l':
            values = [values]
        for i in range(len(values)):
            if values[i] < 0:
                raise ValueError('Minimum chapter is 0')
            if values[i].is_integer():
                values[i] = int(values[i])
            values[i] = str(values[i])
        if self.dest == 'l':
            values = values[0]
        setattr(namespace, self.dest, values)

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('task', choices=['manga', 'doujin', 'merge', 'c2pdf', 'search', 'db', 'check', 'sauce'])
webtoon_type = parser.add_argument_group('download').add_mutually_exclusive_group()
webtoon_type.add_argument('-single', '-code', help='url of the manga, or code of the doujin')
webtoon_type.add_argument('-file', help='downloads webtoons based on the given json file')
mc_options = parser.add_argument_group('merge or convert').add_mutually_exclusive_group()
mc_options.add_argument('-folder', help='merges or converts images in given folder')
mc_options.add_argument('-bulk', help='merges or converts images of folders in the given folder')
mc_options.add_argument('-bulkone', help='converts images of folders in the given folder into one pdf file')
parser.add_argument('-s', nargs='+', metavar='modules', help='specify domains to scrape from')
parser.add_argument('-n', metavar='str', help='specify a name')
parser.add_argument('-m', action='store_true', help='if set, merges images vertically')
parser.add_argument('-fit', action='store_true', help='if set, resizes the images to the same width')
parser.add_argument('-p', action='store_true', help='if set, converts images to a pdf file')
parser.add_argument('-t', type=float, help='set sleep time between requests')
chapters = parser.add_argument_group('specify chapters').add_mutually_exclusive_group()
chapters.add_argument('-c', action=SetChapters, nargs='+', type=float, help='specify chapters')
chapters.add_argument('-l', action=SetChapters, type=float, help='chapters after the given chapter')
chapters.add_argument('-r', action=SetChapters, nargs=2, type=float, metavar=('begin', 'end'), help='chapters between the given chapters')
search_args = parser.add_argument_group('customize search results')
search_args.add_argument('-page-limit', default=3, type=int, help='specify how many pages should be searched')
search_args.add_argument('-absolute', action='store_true', help='if set, checks that the name you searched should be in the title')
saucer = parser.add_argument_group('find source of an image').add_mutually_exclusive_group()
saucer.add_argument('-url', help='url of the image')
saucer.add_argument('-image', help='specify a downloaded image path')
args = parser.parse_args(args=(sys.argv[1:] or ['-h']))

settings.SLEEP_TIME = args.t or settings.SLEEP_TIME
settings.AUTO_MERGE = args.m or settings.AUTO_MERGE
settings.AUTO_PDF_CONVERSION = args.p or settings.AUTO_PDF_CONVERSION
settings.FIT_MERGE = args.fit or settings.FIT_MERGE

if args.task in ['manga', 'doujin', 'search', 'db', 'check']:
    from utils.modules_contributer import get_modules
    args.s = get_modules(args.s)

if (args.single or args.task == 'db') and len(args.s) > 1:
    parser.error('please specify one module using -s argument.\nyou can only set one module when downloading or getting database.')

os.system('color')

match args.task:
    case 'manga':
        if args.file:
            from downloaders.manga_file import download_file
            download_file(args.file)
        elif args.single:
            from downloaders.manga_single import download_single
            download_single(args.n or args.single, args.single, args.s[0], args.l, args.r, args.c)
        else:
            parser.error('please use one of the following arguments: [-single, -file]')

    case 'doujin':
        if args.file:
            from downloaders.doujin_file import download_doujins
            download_doujins(args.file)
        elif args.single:
            from downloaders.doujin_single import download_doujin
            download_doujin(args.single, args.s[0])
        else:
            parser.error('please use one of the following arguments: [-single, -file]')

    case 'merge':
        if args.folder:
            from utils.image_merger import merge_folder
            merge_folder(args.folder, f'Merged/{args.folder}')
        elif args.bulk:
            from utils.image_merger import merge_bulk
            merge_bulk(args.bulk, f'Merged/{args.bulk}')
        else:
            parser.error('please set one of the following arguments: [-folder, -bulk]')

    case 'c2pdf':
        if args.folder:
            if not args.n:
                parser.error('please specify a name for pdf using -n')
            from utils.pdf_converter import convert_folder
            convert_folder(args.folder, args.folder, args.n)
        elif args.bulk:
            from utils.pdf_converter import convert_bulk
            convert_bulk(args.bulk, args.bulk)
        elif args.bulkone:
            from utils.pdf_converter import convert_bulkone
            convert_bulkone(args.bulkone, args.bulkone)
        else:
            parser.error('please set one of the following arguments: [-folder, -bulk, -bulkone]')

    case 'search':
        if not args.n:
            parser.error('you should specify what you want to search using -n')
        from crawlers.search_engine import search_wrapper
        search_wrapper(args.n, args.s, args.absolute, args.page_limit)

    case 'db':
        from crawlers.database_crawler import crawl
        crawl(args.s[0])

    case 'check':
        from utils.module_checker import check_modules
        check_modules(args.s)

    case 'sauce':
        if args.image:
            from utils.saucer import sauce_file, sauce_url
            url = sauce_file(args.image)
            sauce_url(url)
        elif args.url:
            from utils.saucer import sauce_url
            sauce_url(args.url)
        else:
            parser.error('please use one of the following arguments: [-url, -image]')