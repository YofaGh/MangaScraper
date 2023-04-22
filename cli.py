import argparse, sys, os
from utils.assets import SetSource, CheckChapters, LastChapter, RangeOfChapters

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('task', choices=['manga', 'doujin', 'merge', 'c2pdf', 'search', 'db'])
type = parser.add_argument_group('download').add_mutually_exclusive_group()
type.add_argument('-single', '-code', help='url of the manga, or code of the doujin')
type.add_argument('-file', help='downloads everthing in given json file')
mc_options = parser.add_argument_group('merge or convert').add_mutually_exclusive_group()
mc_options.add_argument('-folder', help='merges or converts images in given folder')
mc_options.add_argument('-bulk', help='merges or converts images of folders in the given folder')
parser.add_argument('-s', action=SetSource, nargs='+', metavar='sources', help='specify domains to scrape from')
parser.add_argument('-n', metavar='str', help='specify a name')
parser.add_argument('-m', action='store_true', help='if set, merges images vertically')
parser.add_argument('-p', action='store_true', help='if set, converts images to a pdf file')
parser.add_argument('-t', default=0.1, type=float, help='set sleep time between requests')
chapters = parser.add_argument_group('specify chapters').add_mutually_exclusive_group()
chapters.add_argument('-c', action=CheckChapters, nargs='+', type=float, help='specify chapters')
chapters.add_argument('-l', action=LastChapter, type=float, help='chapters after the given chapter')
chapters.add_argument('-r', action=RangeOfChapters, nargs=2, type=float, metavar=('begin', 'end'), help='chapters between the given chapters')
search_args = parser.add_argument_group('customize search results')
search_args.add_argument('-page-limit', default=1000, type=int, help='specify how many pages should be searched')
search_args.add_argument('-absolute', action='store_true', help='if set, checks that the name you searched should be in the title')
args = parser.parse_args(args=(sys.argv[1:] or ['-h']))

if (args.single or args.task == 'db') and (not args.s or len(args.s) > 1):
    parser.error('please specify one source using -s argument.\nyou can only set one source when downloading or getting database.')

os.system('color')

match args.task:
    case 'manga':
        if args.file:
            from downloaders.manga_file import download_file
            download_file(args.file, args.t, args.m, args.p)
        elif args.single:
            from downloaders.manga_single import download_single
            download_single(args.n or args.single, args.single, args.s[0], args.t, args.l, args.r, args.c, args.m, args.p)
        else:
            parser.error('please use one of the following arguments: [-single, -file]')

    case 'doujin':
        if args.file:
            from downloaders.doujin_file import download_doujins
            download_doujins(args.file, args.t, args.m, args.p)
        elif args.single:
            from downloaders.doujin_single import download_doujin
            download_doujin(args.single, args.s[0], args.t, args.m, args.p)
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
            print('please set one of the following arguments: [-folder, -bulk]')

    case 'c2pdf':
        if args.folder:
            if not args.n:
                parser.error('please specify a name for pdf using -n')
            from utils.pdf_converter import convert_folder
            convert_folder(args.folder, args.folder, args.n)
        elif args.bulk:
            from utils.pdf_converter import convert_bulk
            convert_bulk(args.bulk, args.bulk)
        else:
            print('please set one of the following arguments: [-folder, -bulk]')

    case 'search':
        if not(args.s and args.n):
            parser.error('you should specify source using -s and what you want to search using -n')
        from crawlers.search_engine import search
        search(args.n, args.s, args.t, args.absolute, args.page_limit)

    case 'db':
        from crawlers.datebase_crawler import crawl
        crawl(args.s[0], args.t)