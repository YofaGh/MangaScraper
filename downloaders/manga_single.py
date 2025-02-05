import os
from requests.exceptions import HTTPError, Timeout
from utils.models import Manga
from utils.logger import log, log_over
from settings import AUTO_MERGE, AUTO_PDF_CONVERSION
from utils.exceptions import ImageMergerException, PDFConverterException
from utils.assets import (
    fix_name_for_folder,
    create_folder,
    validate_corrupted_image,
    validate_truncated_image,
    sleep,
)


def download_single(
    manga: str,
    url: str,
    module: Manga,
    last: str | None,
    ranged: tuple[str] | None,
    chapters: list[str] | None,
) -> None:
    chapters_to_download = get_name_of_chapters(
        manga, url, module, last, ranged, chapters
    )
    inconsistencies = download_manga(manga, url, module, chapters_to_download)
    if inconsistencies:
        log(
            f"There were some inconsistencies with the following chapters: {', '.join(inconsistencies)}",
            "red",
        )


def get_name_of_chapters(
    manga: str,
    url: str,
    module: Manga,
    last: str | None,
    ranged: tuple[str] | None,
    c_chapters: list[str] | None,
) -> list[dict[str, str]]:
    ctd = []
    log_over(f"\r{manga}: Getting chapters...")
    chapters = module.get_chapters(url)
    if last:
        reached_last_downloaded_chapter = False
        for chapter in chapters:
            if last in chapter["name"]:
                reached_last_downloaded_chapter = True
                continue
            if reached_last_downloaded_chapter:
                ctd.append(chapter)
    elif ranged:
        reached_beginning_chapter = False
        for chapter in chapters:
            if ranged[0] in chapter["name"]:
                reached_beginning_chapter = True
            if reached_beginning_chapter:
                ctd.append(chapter)
            if ranged[1] in chapter["name"]:
                break
    elif c_chapters:
        for c in c_chapters:
            for chapter in chapters:
                if c in chapter["name"]:
                    ctd.append(chapter)
                    break
    else:
        ctd = chapters
    log(f"\r{manga}: {len(ctd)} chapter{'' if len(ctd) == 1 else 's'} to download.")
    return ctd


def download_manga(
    manga: str, url: str, module: Manga, chapters: list[dict[str, str]]
) -> list[str]:
    inconsistencies = []
    last_truncated = None
    fixed_manga = fix_name_for_folder(manga)
    create_folder(fixed_manga)
    while chapters:
        try:
            chapter_name = chapters[0]["name"]
            log_over(f"\r{manga}: {chapter_name}: Getting image links...")
            images, save_names = module.get_images(url, chapters[0])
            log_over(f"\r{manga}: {chapter_name}: Creating folder...")
            path = f"{fixed_manga}/{fix_name_for_folder(chapter_name)}"
            create_folder(path)
            adder = 0
            i = 0
            while i < len(images):
                log_over(
                    f"\r{manga}: {chapter_name}: Downloading image {i + adder + 1}/{len(images) + adder}..."
                )
                if save_names:
                    save_path = f"{path}/{save_names[i]}"
                else:
                    if str(i + adder + 1) not in images[i].split("/")[-1]:
                        adder += 1
                        inconsistencies.append(
                            f"{manga}/{chapter_name}/{i + adder:03d}.{images[i].split('.')[-1]}"
                        )
                        log(
                            f" Warning: Inconsistency in order of images!!!. Skipped image {i + adder}",
                            "red",
                        )
                        log_over(
                            f"\r{manga}: {chapter_name}: Downloading image {i + adder + 1}/{len(images) + adder}..."
                        )
                    save_path = f"{path}/{i + adder + 1:03d}.{images[i].split('.')[-1]}"
                if not os.path.exists(save_path):
                    sleep()
                    saved_path = module.download_image(images[i], save_path)
                    if not saved_path:
                        log(
                            f" Warning: Image {i + adder + 1} could not be downloaded. url: {images[i]}",
                            "red",
                        )
                    elif not validate_corrupted_image(saved_path):
                        log(
                            f" Warning: Image {i + adder + 1} was corrupted. may not be able to merge this chapter.",
                            "red",
                        )
                    elif (
                        not validate_truncated_image(saved_path)
                        and last_truncated != saved_path
                    ):
                        last_truncated = saved_path
                        os.remove(saved_path)
                        log(
                            f" Warning: Image {i + adder + 1} was truncated. trying to download it one more time...",
                            "red",
                        )
                        continue
                i += 1
            log(
                f"\r{manga}: {chapter_name}: Finished downloading, {len(images)} images were downloaded.",
                "green",
            )
            del chapters[0]
            if AUTO_MERGE:
                from utils.image_merger import merge_folder

                merge_folder(path, f"Merged/{path}", f"{manga}: {chapter_name}")
            if AUTO_PDF_CONVERSION:
                from utils.pdf_converter import convert_folder

                convert_folder(
                    path,
                    fixed_manga,
                    f"{manga}_{chapter_name}",
                    f"{manga}: {chapter_name}",
                )
        except (
            Timeout,
            HTTPError,
            ImageMergerException,
            PDFConverterException,
        ) as error:
            log(error, "red")
    return inconsistencies
