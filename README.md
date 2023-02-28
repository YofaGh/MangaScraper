# Manga/Manhua Scraper

> - Download your favorite comics.
> - Search between sources.
> - Merge downloaded chapters into one or two images.
> - And convert them into PDF format.

## Table of Contents

- [command line interface](#command-line-interface)

- [modules](#modules)

- [download single manga](#download-single-manga)

- [download mangas of a file](#download-mangas-of-a-file)

- [download a doujin by it's code](#download-a-doujin-by-its-code)

- [image merger](#image-merger)

- [pdf converter](#pdf-converter)

- [search engine](#search-engine)

## Command Line Interface
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

## Download Single Manga
>
> When downloading a single manga using do_single.py, following informations should be provided:
>
> - source of manga
> - url of manga
> - chapters you want to download(which can be set with [-a, -l, -r, -c] arguments)
> - Name of the Manga and merging args are optional

## Download mangas of a file
>
> When downloading more than one manga using do_file.py you should specify name of a json file.  
> Json file will be automatically updated after each chapter is downloaded.  
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

## Download a Doujin by It's Code
>
> You can download a doujin from an implemented module just by entering its code.  
> Note: Doujins are still in development.  

## Image merger
>
> You can merge all chapters of a manga, a single chapter or any folder that has images in it.  
> before starting the merge process, all the images will be validated to avoid any exception.

## PDF Converter
>
> You can also convert the chapters to PDF to read them better.  
> converting chapters that are merged into fewer images is highly recommended.

## Search Engine
>
> Still in development but allows you to search between available sources.
