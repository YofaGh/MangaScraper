# Manga/Manhua Scraper

> - Download your favorite Webtoons.
> - Search between varoius websites.
> - Merge downloaded Webtoons into one or two images.
> - Convert downloaded Webtoons into PDF file.
> - Search and find what you want.
> - Download full database of a website.

## Table of Contents

- [Setup](#setup)

- [Command line interface](#command-line-interface)

- [Modules](#modules)

- [Download a single manga](#download-a-single-manga)

- [Download mangas of a file](#download-mangas-of-a-file)

- [Download a doujin by it's code](#download-a-doujin-by-its-code)

- [Download doujins of a file](#download-doujins-of-a-file)

- [Image merger](#image-merger)

- [PDF converter](#pdf-converter)

- [Search engine](#search-engine)

- [Database crawler](#database-crawler)

- [Modules Checker](#modules-checker)

## Setup

> - After cloning the repository use ```pip install -r requirements.txt``` to install requirements.
> - List of implemented modules is available in implemented_modules.txt file.

## Command line interface
>
> Command center gives you various options like:
>
> - download a single manga/manhua/doujin or multiple.
> - automatically merge them and convert them into pdf using -m.
> - if you also set -rS, images will get merged and resized so the overall width will be equal and no white space will abe added to final images.
> - change the time sleep between each request.
> - merge images of a single folder or subfolders of a folder.
> - convert images of a single folder or subfolders of a folder to pdf file.
> - search in websites using implemented modules.
> - set the chapter numbers to download when downloading a single manga.
> - you can use -t argument to set the sleep time between each request. the default is 0.1 sec.

## Modules
>
> There are various modules implemented so far. They inherit from models.  
> They're implemented differently based on how the website is develpoed.  
> In case if using custom user agents or cookies are required, sending requests to the webiste is done dirctly by the module itself.  
> To use them, they're imported in modules_contributer.py and can be accesed by get_module function.  

## Download a single manga
>
> When downloading a single manga using manga -single, a module and a url should be provided.  
> You can specify which chapters to download using [-l, -r, -c] arguments.  
> By default all chapters will be downloaded.  
> Name of the Manga and merging args are optional.  
>
> Examples:
>
> - all chapters: ```python cli.py manga -single 11643-attack-on-titan -s mangapark.to```  
> - chapters after a certian chapter: ```python cli.py manga -single secret-class -s manhuscan.us -l 52```  
> - chapters between two chapters: ```python cli.py manga -single secret-class -s manhuscan.us -r 20 30```  
> - specify chapters: ```python cli.py manga -single secret-class -s manhuscan.us -c 5 10 36```  
> - e.g. ```python cli.py manga -single secret-class -s manhuscan.us -n "Secret Class" -m -p```

## Download mangas of a file
>
> Let's say you read a couple of mangas that are updated on weekly basis and you want to download all new chapters, then you should go with -file option.  
> When downloading more than one manga using manga_file.py you should specify name of a json file.  
> Json file will be automatically updated after each chapter is downloaded.  
> Example: ```python cli.py manga -file mangas.json```  
> Format of the json file should look like this:

```json
{
    "Attck on Titan": {
        "include": true,
        "domain": "mangapark.to",
        "url": "11643-attack-on-titan",
        "last_downloaded_chapter": null,
        "chapters": []
    },
    "Secret Class": {
        "include": true,
        "domain": "manhuascan.us",
        "url": "secret-class",
        "last_downloaded_chapter": "chapter-100",
        "chapters": []
    },
    "Solo Leveling": {
        "include": true,
        "domain": "manga68.com",
        "url": "one-piece",
        "last_downloaded_chapter": "pass",
        "chapters": [
            "chapter-1",
            "chapter-2"
        ]
    }
}
```

> - if the "last_downloaded_chapter" is null, all of the chapters will be added to the download list.  
> - if the "last_downloaded_chapter" has valid value, do_file.py will automatically add the chapters after "last_downloaded_chapter" to the download list.  
> - and if the "last_downloaded_chapter" is equal to "pass", only the download list which user filled will be downloaded.

## Download a doujin by it's code
>
> You can download a doujin from an implemented module just by entering its code.  
> Note: Doujins are still in development.  
> Example: ```python cli.py doujin -code 000000 -s hentaifox.com```  

## Download doujins of a file
>
> If you have a couple of codes and want to download all of them at once you can put them in a json file like the one down below and use -file option.  
> When downloading more than one doujin using doujin_file.py you should specify name of a json file.  
> Json file will be automatically updated after each doujin is downloaded.  
> Example: ```python cli.py doujin -file doujins.json```  
> Format of the json file should look like this:

```json
{
    "nyahentai.red": {
        "codes": [
            999999,
            999998
        ]
    },
    "hentaifox.com": {
        "codes": [
            999997,
            999996
        ]
    }
}
```

## Image merger
>
> You can merge all chapters of a manga or any folder that has images in it vertically.  
> before starting the merge process, all the images will be validated to avoid any exception.  
> Examples:  
>
> - mrege an entire manga: ```python cli.py merge -bulk "One Piece"```  
> - mrege a folder: ```python cli.py merge -folder "path/to/folder"```  
> - mrege a folder and resize it: ```python cli.py merge -folder "path/to/folder" -rS```  

## PDF converter
>
> You can also convert the chapters to PDF to read them better.  
> before starting the merge process, all the images will be validated to avoid any exception.  
> converting chapters that are merged into fewer images is highly recommended.  
> Examples:  
>
> - convert an entire manga: ```python cli.py c2pdf -bulk "One Piece"```  
> - convert a folder: ```python cli.py convert -folder "path/to/folder" -n "pdf_name.pdf"```  

## Search engine
>
> allows you to search between available modules that searching function is implemented for them.  
> unlike downloading with -single argument you can specify multiple modules when using -s.  
> you can also use "-s all" to search in all modules.  
> set page limit with -page-limit argument.  
> you can limit the results with setting -absoulte argument.  
> Examples:  
>
> - search in one module: ```python cli.py search -s manhuascan.us -n "secret"```  
> - search in multiple modules: ```python cli.py search -s mangapark.to manga68.com -n "secret"```  
> - search in all modules: ```python cli.py search -s all -n "secret"```  
> - e.g.  ```python cli.py search -s manhuascan.us -n "secret" -page-limit 5 -absolute -t 1```

## Database crawler
>
> allows you to download databse of modules that get_db function is implemented for them.  
> you can only get database of one module at a time.  
> result of the crawling will be saved to a json file with module name on it.  
> Examples:  ```python cli.py db -s manhuascan.us```

## Modules Checker
>
> To check if a module is functional or not you can use check option.  
> Examples:  
>
> - check on module: ```python cli.py check -s manhuascan.us```
> - check all modules: ```python cli.py check -s all```  
