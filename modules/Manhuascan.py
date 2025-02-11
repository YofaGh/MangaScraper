from utils.models import Manga


class Manhuascan(Manga):
    domain = "manhuascan.us"
    logo = "https://manhuascan.us/fav.png?v=1"

    def get_info(manga):
        from contextlib import suppress

        response, _ = Manhuascan.send_request(f"https://manhuascan.us/manga/{manga}")
        soup = Manhuascan.get_html_parser(response.text)
        (
            cover,
            title,
            alternative,
            summary,
            rating,
            status,
            authors,
            artists,
            posted_on,
            updated_on,
        ) = 10 * [""]
        info_box = soup.find("div", {"class": "tsinfo bixbox"})
        with suppress(Exception):
            cover = soup.find("img", {"class": "attachment- size- wp-post-image"})[
                "src"
            ]
        with suppress(Exception):
            title = soup.find("h1", {"class": "entry-title"}).get_text(strip=True)
        with suppress(Exception):
            alternative = (
                soup.find("span", {"class": "alternative"})
                .get_text(strip=True)
                .replace("Other Name: ", "")
            )
        with suppress(Exception):
            summary = soup.find(
                "div", {"class": "entry-content entry-content-single"}
            ).get_text(strip=True)
        with suppress(Exception):
            rating = float(
                soup.find("div", {"class": "detail_rate"})
                .find("span")
                .get_text(strip=True)
                .replace("/5", "")
            )
        with suppress(Exception):
            status = (
                info_box.find(lambda tag: "Status" in tag.text)
                .find("i")
                .get_text(strip=True)
            )
        with suppress(Exception):
            authors = (
                info_box.find(lambda tag: "Author" in tag.text)
                .find("a")
                .get_text(strip=True)
            )
        with suppress(Exception):
            artists = (
                info_box.find(lambda tag: "Artist" in tag.text)
                .find("a")
                .get_text(strip=True)
            )
        with suppress(Exception):
            posted_on = info_box.find(lambda tag: "Posted" in tag.text).find("time")[
                "datetime"
            ]
        with suppress(Exception):
            updated_on = info_box.find(lambda tag: "Updated" in tag.text).find("time")[
                "datetime"
            ]
        return {
            "Cover": cover,
            "Title": title,
            "Alternative": alternative,
            "Summary": summary,
            "Rating": rating,
            "Status": status,
            "Extras": {"Authors": authors, "Artists": artists},
            "Dates": {"Posted On": posted_on, "Updated On": updated_on},
        }

    def get_chapters(manga):
        response, _ = Manhuascan.send_request(f"https://manhuascan.us/manga/{manga}")
        soup = Manhuascan.get_html_parser(response.text)
        divs = soup.find_all("div", {"class": "eph-num"})
        chapters_urls = [div.find("a")["href"].split("/")[-1] for div in divs[::-1]]
        chapters = [
            {"url": chapter_url, "name": Manhuascan.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(manga, chapter):
        response, _ = Manhuascan.send_request(
            f"https://manhuascan.us/manga/{manga}/{chapter['url']}"
        )
        soup = Manhuascan.get_html_parser(response.text)
        images = soup.find("div", {"id": "readerarea"}).find_all("img")
        images = [image["src"] for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError

        page = 1
        session = None
        while True:
            try:
                response, session = Manhuascan.send_request(
                    f"https://manhuascan.us/manga-list?search={keyword}&page={page}",
                    session=session,
                )
            except HTTPError:
                yield {}
            soup = Manhuascan.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "bsx"})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find("a")["title"]
                if absolute and keyword.lower() not in ti.lower():
                    continue
                latest_chapter = ""
                with suppress(Exception):
                    latest_chapter = (
                        manga.find("div", {"class": "adds"})
                        .find("a")["href"]
                        .split("/")[-1]
                    )
                results[ti] = {
                    "domain": Manhuascan.domain,
                    "url": manga.find("a")["href"].split("/")[-1],
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("img")["src"],
                    "page": page,
                }
            yield results
            page += 1

    def get_db():
        return Manhuascan.search_by_keyword("", False)
