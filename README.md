# Manga/Manhua Scraper

A powerful command-line tool for downloading, managing, and converting manga and manhua from various websites.

## Features

- Download your favorite manga and webtoons from multiple sources
- Search across various supported websites
- Merge downloaded content into single or paired images
- Convert downloads into PDF files for easier reading
- Find the source of manga/manhua images
- Download entire website databases
- Customize download parameters including chapter ranges

## Table of Contents

- [Setup](#setup)
- [Command Line Interface](#command-line-interface)
- [Modules](#modules)
- [Usage Guide](#usage-guide)
  - [Download a Single Manga](#download-a-single-manga)
  - [Download Multiple Manga From a File](#download-multiple-manga-from-a-file)
  - [Download a Doujin by Code](#download-a-doujin-by-code)
  - [Download Multiple Doujins From a File](#download-multiple-doujins-from-a-file)
  - [Image Merger](#image-merger)
  - [PDF Converter](#pdf-converter)
  - [Search Engine](#search-engine)
  - [Database Crawler](#database-crawler)
  - [Sauce Finder](#sauce-finder)
  - [Module Checker](#module-checker)

## Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the tool using the command line interface

A list of all implemented modules is available in the [modules.yaml](modules.yaml) file.

## Command Line Interface

The command center offers various options:

- Download a single manga/manhua/doujin or multiple series
- Automatically merge images and convert them to PDF using `-m`
- Resize and merge images with the `-fit` flag to eliminate white space
- Adjust request frequency with the `-t` parameter (default: 0.1 seconds)
- Merge images of a single folder or subfolders
- Convert images to PDF for individual folders or subfolders
- Search across supported websites
- Specify chapter ranges for downloading

## Modules

The scraper uses various modules that inherit from base models. Each module is implemented according to the target website's structure. When a website requires custom user agents or cookies, the module handles the request process directly.

Modules are loaded from the [modules.yaml](modules.yaml) file through [modules_contributer.py](utils/modules_contributer.py) and can be accessed using the `get_modules` function.

## Usage Guide

### Download a Single Manga

Use the `-single` flag with a module and URL to download a manga. You can specify chapter ranges using the `-l`, `-r`, or `-c` arguments.

**Examples:**

```bash
# Download all chapters
python cli.py manga -single 11643-attack-on-titan -s mangapark.to

# Download chapters after chapter 52
python cli.py manga -single secret-class -s manhuscan.us -l 52

# Download chapters between 20 and 30
python cli.py manga -single secret-class -s manhuscan.us -r 20 30

# Download specific chapters (5, 10, and 36)
python cli.py manga -single secret-class -s manhuscan.us -c 5 10 36

# Download with custom name and merge into PDF
python cli.py manga -single secret-class -s manhuscan.us -n "Secret Class" -m -p
```

### Download Multiple Manga From a File

For managing multiple manga titles, use the `-file` option with a JSON file. The file is automatically updated after each chapter download.

**Example:**

```bash
python cli.py manga -file mangas.json
```

**JSON Format:**

```json
{
    "Attack on Titan": {
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
        "last_downloaded_chapter": {
            "url": "chapter-100",
            "name": "Chapter 100"
        },
        "chapters": []
    }
}
```

Notes:

- If `last_downloaded_chapter` is `null`, all chapters will be downloaded
- If `last_downloaded_chapter` has a value, only newer chapters will be downloaded

### Download a Doujin by Code

Use the `-code` or `-single` flag to download a single doujin by its code.

**Example:**

```bash
python cli.py doujin -code 000000 -s hentaifox.com
```

### Download Multiple Doujins From a File

Download multiple doujins using a JSON file with the `-file` option.

**Example:**

```bash
python cli.py doujin -file doujins.json
```

**JSON Format:**

```json
{
    "nyahentai.red": [
        999999,
        999998
    ],
    "hentaifox.com": [
        999997,
        999996
    ]
}
```

### Image Merger

Merge images vertically, either for an entire manga or specific folders. Images are validated before processing.

**Examples:**

```bash
# Merge an entire manga
python cli.py merge -bulk "One Piece"

# Merge a folder
python cli.py merge -folder "path/to/folder"

# Merge a folder and resize to eliminate white space
python cli.py merge -folder "path/to/folder" -fit
```

### PDF Converter

Convert chapters to PDF format for easier reading. Works best with previously merged images.

**Examples:**

```bash
# Convert an entire manga
python cli.py c2pdf -bulk "One Piece"

# Convert a folder with a custom name
python cli.py convert -folder "path/to/folder" -n "pdf_name.pdf"
```

### Search Engine

Search for manga across available modules.

**Examples:**

```bash
# Search in one module
python cli.py search -s manhuascan.us -n "secret"

# Search in multiple modules
python cli.py search -s mangapark.to manga68.com -n "secret"

# Search in all modules
python cli.py search -n "secret"

# Advanced search with page limit and timeout
python cli.py search -s manhuascan.us -n "secret" -page-limit 5 -absolute -t 1
```

### Database Crawler

Download the database of a module. Results are saved as a JSON file named after the module.

**Example:**

```bash
python cli.py db -s manhuascan.us
```

### Sauce Finder

Find the source of a manga/manhua image.

**Examples:**

```bash
# Find source using a local image file
python cli.py sauce -image "path/to/image"

# Find source using an image URL
python cli.py sauce -url "url/to/image"
```

### Module Checker

Check if modules are functioning correctly.

**Examples:**

```bash
# Check a specific module
python cli.py check -s manhuascan.us

# Check all modules
python cli.py check
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
