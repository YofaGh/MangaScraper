# Manga/Manhua Scraper

> - Download your favorite comics.
> - Search between sources.
> - Merge downloaded chapters into one or two images.
> - And convert them into PDF format.

## Table of Contents
* [command line interface](#command-line-interface)
* [sources](#sources)
* [download single manga](#download-single-manga)
* [download mangas of a file](#download-mangas-of-a-file)
* [image merger](#image-merger)
* [pdf converter](#pdf-converter)
* [search engine](#search-engine)

## Command Line Interface
> Command center gives you various options like:
> - download a single manga or multiple
> - automatically merge them and convert them into pdf
> - change the time sleep between each request
> - merge a downloaded chapter or manga
> - set the chapter numbers to download when downloading a single manga

## Sources
> There are various sources implemented so far. They inherit from M_Manga class.  
> They're implemented differently based on the website's source code.  
> To use them, they're included in sources_dict in assets.py file.

## Download Single Manga
> When downloading a single manga using do_single.py, following informations should be provided:
> - source of manga
> - url of manga
> - chapters you want to download. which can be set with [-a, -l, -r, -c] arguments.
> - Name of the Manga and merging args are optional.

## Download mangas of a file
> When downloading a single manga using do_file.py you should specify name of a json file
> Format of the json file should look like this:
```json
{
    "Secret Class": {
        "include": true,
        "domain": "manhuascan.us",
        "url": "secret-class",
        "last_downloaded_chapter": "chapter-100",
        "chapters": []
    },
    "Boarding Diary": {
        "include": true,
        "domain": "manhuascan.us",
        "url": "boarding-diary",
        "last_downloaded_chapter": null,
        "chapters": []
    },
    "Brave New World": {
        "include": true,
        "domain": "manhuascan.us",
        "url": "a-wonderful-new-world",
        "last_downloaded_chapter": "pass",
        "chapters": [
            "chapter-1",
            "chapter-2"
        ]
    }
}
```
> - if the "last_downloaded_chapter" has valid value, do_file.py will automatically add the chapters after "last_downloaded_chapter" to the download list
> - if the "last_downloaded_chapter" is null, all of the chapters will be added to the download list
> - and if the "last_downloaded_chapter" is equal to "pass", only the download list which user filled will be downloaded.

## Image merger
> You can merge all chapters of a manga, a single chapter or any folder that has images in it.  
> before starting the merge process, all the images will be validated to avoid any exception.

## PDF Converter
> You can also convert the chapters to PDF to read them better.  
> converting chapters that are merged into fewer images is highly recommended.

## Search Engine
> Still in development but allows you search between available sources.