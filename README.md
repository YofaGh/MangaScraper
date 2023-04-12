# Manga/Manhua Scraper

> - Download your favorite comics.
> - Search between sources.
> - Merge downloaded chapters into one or two images.
> - Convert downloaded chapters into PDF file.
> - Search and find what you want.

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

## Setup

> - After cloning the repository use ```pip install -r requirements.txt``` to install requirements.
> - Lists of implemented modules are available in implemented_modules.txt file.

## Command line interface
>
> Command center gives you various options like:
>
> - download a single manga/manhua/doujin or multiple.
> - automatically merge them and convert them into pdf.
> - change the time sleep between each request.
> - merge images of a single folder or subfolders of a folder.
> - convert images of a single folder or subfolders of a folder to pdf file.
> - search in websites using implemented modules
> - set the chapter numbers to download when downloading a single manga.
> - you can use -t argument to set the sleep time between each request. the default is 0.1 sec.

## Modules
>
> There are various modules implemented so far. They inherit from Base classes.  
> They're implemented differently based on the website's source code.  
> In case if using custom user agents or cookies are needed, sending requests to the source is done dirctly by the source class itself.  
> To use them, they're imported in modules_contributer.py and can be accesed by get_class function.

## Download a single manga
>
> When downloading a single manga using manga_single.py, the following informations should be provided:
>
> - source of manga
> - url of manga
> - chapters you want to download(which can be set with [-a, -l, -r, -c] arguments)
>
> Name of the Manga and merging args are optional  
>
> Examples:
>
> - all chapters: ```python cli.py manga -single attack-on-titan -s truemanga.com -a```  
> - chapters after a certian chapter: ```python cli.py manga -single attack-on-titan -s truemanga.com -l 52```  
> - chapters between two chapters: ```python cli.py manga -single attack-on-titan -s truemanga.com -r 20 30```  
> - specify chapters: ```python cli.py manga -single attack-on-titan -s truemanga.com -c 5 10 36```  
> - e.g. ```python cli.py manga -single attack-on-titan -s truemanga.com -n "Attack on Titan" -a -m -p```

## Download mangas of a file
>
> When downloading more than one manga using manga_file.py you should specify name of a json file.  
> Json file will be automatically updated after each chapter is downloaded.  
> Example: ```python cli.py manga -file mangas.json```  
> Format of the json file should look like this:

```json
{
    "Attck on Titan": {
        "include": true,
        "domain": "truemanga.com",
        "url": "attack-on-titan",
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
    "One Piece": {
        "include": true,
        "domain": "truemanga.com",
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
> When downloading more than one doujin using doujin_file.py you should specify name of a json file.  
> Json file will be automatically updated after each doujin is downloaded.  
> Example: ```python cli.py doujin -file doujins.json```  
> Format of the json file should look like this:

```json
{
    "nyahentai.red": {
        "codes": [
            000000,
            111111
        ]
    },
    "hentaifox.com": {
        "codes": [
            222222,
            333333
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
> allows you to search between available sources that searching function is implemented for them.  
> unlike downloading with -single argument you can specify multiple sources when using -s.  
> you can also use "-s all" to search in all modules.  
> set page limit with -page-limit argument.  
> you can limit the results with setting -absoulte argument.  
> Examples:  
>
> - search in one module: ```python cli.py search -s manhuascan.us -n "secret"```  
> - search in multiple modules: ```python cli.py search -s truemanga.com mangareader.cc -n "secret"```  
> - search in all modules: ```python cli.py search -s all -n "secret"```  
> - e.g.  ```python cli.py search -s manhuascan.us -n "secret" -page-limit 5 -absolute -t 1```
