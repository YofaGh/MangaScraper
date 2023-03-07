# Manga/Manhua Scraper

> - Download your favorite comics.
> - Search between sources.
> - Merge downloaded chapters into one or two images.
> - And convert them into PDF format.

## Table of Contents

- [Setup](#setup)

- [Command line interface](#command-line-interface)

- [Modules](#modules)

- [Download a single manga](#download-a-single-manga)

- [Download mangas of a file](#download-mangas-of-a-file)

- [Download a Doujin by it's code](#download-a-doujin-by-its-code)

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
> - download a single manga or multiple.
> - automatically merge them and convert them into pdf.
> - change the time sleep between each request.
> - merge a downloaded chapter or manga.
> - set the chapter numbers to download when downloading a single manga.

## Modules
>
> There are various modules implemented so far. They inherit from Base classes.  
> They're implemented differently based on the website's source code.  
> In case if using custom user agents or cookies are needed, sending requests to the source is done dirctly by the source class itself.  
> To use them, they're imported in modules_contributer.py and can be accesed by contributer function.

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
> - all chapters: ```python cli.py -u attack-on-titan -s truemanga.com -a```  
> - all chapters after a certian chapter: ```python cli.py -u attack-on-titan -s truemanga.com -l 52```  
> - all chapters between two chapters: ```python cli.py -u attack-on-titan -s truemanga.com -r 20 30```  
> - specify chapters: ```python cli.py -u attack-on-titan -s truemanga.com -c 5 10 36```  
> - e.g. ```python cli.py -u attack-on-titan -s truemanga.com -n "Attack on Titan" -a -g -p```

## Download mangas of a file
>
> When downloading more than one manga using manga_file.py you should specify name of a json file.  
> Json file will be automatically updated after each chapter is downloaded.  
> Example: ```python cli.py -f mangas.json```  
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

## Download a Doujin by it's code
>
> You can download a doujin from an implemented module just by entering its code.  
> Note: Doujins are still in development.  
> Example: ```python cli.py -doujin 000000 -s hentaifox.com```  

## Image merger
>
> You can merge all chapters of a manga, a single chapter or any folder that has images in it vertically.  
> before starting the merge process, all the images will be validated to avoid any exception.  
> Examples:  
>
> - mrege an entire manga: ```python cli.py -mergemanga "One Piece"```  
> - mrege a chapter: ```python cli.py -mergechapter "One Piece" -c 20 21 22```  
> - mrege a folder: ```python cli.py -mergefolder "path/to/folder"```  

## PDF converter
>
> You can also convert the chapters to PDF to read them better.  
> converting chapters that are merged into fewer images is highly recommended.

## Search engine
>
> Still in development but allows you to search between available sources.
