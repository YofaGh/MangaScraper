from utils.logger import log_over, log
from utils.modules_contributer import get_modules
from utils.exceptions import MissingModuleException
from utils.assets import save_json_file, load_json_file


def download_file(json_file: str) -> None:
    get_name_of_chapters(json_file)
    inconsistencies = download_mangas(json_file)
    if inconsistencies:
        log(
            f"There were some inconsistencies with the following chapters: {', '.join(inconsistencies)}",
            "red",
        )


def get_name_of_chapters(json_file: str) -> None:
    mangas = load_json_file(json_file)
    valid_mangas = [manga for (manga, detm) in mangas.items() if detm["include"]]
    for valid_manga in valid_mangas:
        manga = mangas[valid_manga]
        log_over(f"\r{valid_manga}: Getting chapters...")
        chapters = get_modules(manga["domain"]).get_chapters(manga["url"])
        if manga["last_downloaded_chapter"]:
            reached_last_downloaded_chapter = False
            for chapter in chapters:
                if chapter["url"] == manga["last_downloaded_chapter"]["url"]:
                    reached_last_downloaded_chapter = True
                    continue
                if reached_last_downloaded_chapter and chapter not in manga["chapters"]:
                    manga["chapters"].append(chapter)
        else:
            manga["chapters"].extend(chapters)
        log(
            f"\r{valid_manga}: {len(manga['chapters'])} chapter{'' if len(manga['chapters']) == 1 else 's'} to download."
        )
    save_json_file(json_file, mangas)


def download_mangas(json_file: str) -> list[str]:
    from downloaders.manga_single import download_manga

    mangas = load_json_file(json_file)
    inconsistencies = []
    valid_mangas = [
        manga
        for (manga, detm) in mangas.items()
        if (detm["include"] and detm["chapters"])
    ]
    for manga in valid_mangas:
        try:
            while mangas[manga]["chapters"]:
                chapter = mangas[manga]["chapters"][0]
                module = get_modules(mangas[manga]["domain"])
                inconsistencies += download_manga(
                    manga, mangas[manga]["url"], module, [chapter]
                )
                mangas[manga]["last_downloaded_chapter"] = chapter
                del mangas[manga]["chapters"][0]
                save_json_file(json_file, mangas)
        except MissingModuleException as error:
            log(error, "red")
    return inconsistencies
