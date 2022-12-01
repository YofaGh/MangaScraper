import argparse
from assets import SetSource, CheckChapters, LastChapter, RangeOfChapters

parser = argparse.ArgumentParser(allow_abbrev=False)
task = parser.add_mutually_exclusive_group()
task.add_argument('-u', action='store', help='url of the manga')
task.add_argument('-f', action='store', help='downloads chapters specified in given json file')
merging_options = parser.add_mutually_exclusive_group()
merging_options.add_argument('-mergefolder', action='store', help='merges images in given folder')
merging_options.add_argument('-mergechapter', action='store', help='merges given chapter')
merging_options.add_argument('-mergemanga', action='store', help='merges all chapters of given manga')
parser.add_argument('-s', action=SetSource, help='domain to scrap from')
parser.add_argument('-c', action=CheckChapters, nargs='+', type=float, help='specify chapters')
parser.add_argument('-n', action='store', help='specifie name of mangas folder')
parser.add_argument('-p', nargs='?', action='store', const='$', help='converts image to pdf to the given path. by default, it creates pdf in each chapter')
parser.add_argument('-g', action='store_true', help='if set, merges images vertically')
single_manga_chapters = parser.add_mutually_exclusive_group()
single_manga_chapters.add_argument('-a', action='store_true', help='all chapters')
single_manga_chapters.add_argument('-l', action=LastChapter, type=float, help='all chapters after the given chapter')
single_manga_chapters.add_argument('-r', action=RangeOfChapters, nargs=2, type=float, help='all chapters between the given chapters')
args = parser.parse_args()

if (args.f or args.mergemanga or args.mergefolder) and (args.c or args.n or args.r or args.l or args.a or args.s):
    parser.error('arguments: [c, n, r, l, a, s] can only be used with -u')

if args.u and not args.s:
    parser.error('argument s is required when using argument u')

if args.mergechapter and (args.n or args.r or args.l or args.a or args.s):
    parser.error('arguments: [n, r, l, a, s] can only be used with -u')

if args.mergechapter and not args.c:
    parser.error('please specify chapter alongside the manga folder with -c argument')

if args.f:
    from do_file import download_file
    download_file(args.f, args.g, args.p)

elif args.u:
    from do_single import download_single
    download_single(args.n or args.u, args.u, args.s, args.a, args.l, args.r, args.c, args.g)

elif args.mergechapter:
    from image_merger import merge_chapter
    for chapter in args.c:
        merge_chapter(args.mergechapter, chapter)

elif args.mergemanga:
    from image_merger import merge_manga
    merge_manga(args.mergemanga)

elif args.mergefolder:
    from image_merger import merge_folder
    merge_folder(args.mergefolder, f'Merged/{args.mergefolder}')

else:
    parser.error('at least one argument is required')