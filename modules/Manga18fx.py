from utils.models import Manga


class Manga18fx(Manga):
    domain = "manga18fx.com"
    logo = "https://manga18fx.com/images/favicon-160x160.jpg"

    def get_info(manga):
        from contextlib import suppress

        response, _ = Manga18fx.send_request(f"https://manga18fx.com/manga/{manga}")
        soup = Manga18fx.get_html_parser(response.text)
        cover, title, alternative, summary, rating, status = 6 * [""]
        extras = {}
        info_box = soup.find("div", {"class": "tab-summary"})
        with suppress(Exception):
            cover = info_box.find("img")["data-src"]
        with suppress(Exception):
            title = (
                soup.find("div", {"class": "post-title"})
                .find("h1")
                .get_text(strip=True)
            )
        with suppress(Exception):
            summary = soup.find("div", {"class": "dsct"}).get_text(strip=True)
        with suppress(Exception):
            rating = float(
                info_box.find("span", {"class": "avgrate"}).get_text(strip=True)
            )
        with suppress(Exception):
            status = (
                info_box.find("div", {"class": "post-status"})
                .find_all("div", {"class": "summary-content"})[1]
                .get_text(strip=True)
            )
        for box in soup.find("div", {"class": "post-content"}).find_all(
            "div", {"class": "post-content_item"}
        ):
            if "Rating" in box.get_text(strip=True):
                continue
            elif "Alternative" in box.get_text(strip=True):
                with suppress(Exception):
                    alternative = box.find(
                        "div", {"class": "summary-content"}
                    ).get_text(strip=True)
            else:
                heading = (
                    box.find("div", {"class": "summary-heading"})
                    .get_text(strip=True)
                    .replace("(s)", "")
                )
                info = box.find("div", {"class": "summary-content"})
                if info.find("a"):
                    extras[heading] = [
                        a.get_text(strip=True) for a in info.find_all("a")
                    ]
                else:
                    extras[heading] = box.find(
                        "div", {"class": "summary-content"}
                    ).get_text(strip=True)
        return {
            "Cover": cover,
            "Title": title,
            "Alternative": alternative,
            "Summary": summary,
            "Rating": rating,
            "Status": status,
            "Extras": extras,
        }

    def get_chapters(manga):
        response, _ = Manga18fx.send_request(f"https://manga18fx.com/manga/{manga}")
        soup = Manga18fx.get_html_parser(response.text)
        divs = soup.find_all("li", {"class": "a-h"})
        chapters_urls = [div.find("a")["href"].split("/")[-1] for div in divs[::-1]]
        chapters = [
            {"url": chapter_url, "name": Manga18fx.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(manga, chapter):
        response, _ = Manga18fx.send_request(
            f"https://manga18fx.com/manga/{manga}/{chapter['url']}"
        )
        soup = Manga18fx.get_html_parser(response.text)
        images = soup.find("div", {"class": "read-content"}).find_all("img")
        images = [image["src"].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from requests.exceptions import HTTPError
        from contextlib import suppress

        template = (
            f"https://manga18fx.com/search?q={keyword}&page=P_P_P_P"
            if keyword
            else "https://manga18fx.com/page/P_P_P_P"
        )
        page = 1
        prev_page = []
        session = None
        while True:
            try:
                response, session = Manga18fx.send_request(
                    template.replace("P_P_P_P", str(page)), session=session
                )
            except HTTPError:
                yield {}
            soup = Manga18fx.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "page-item"})
            results = {}
            if mangas == prev_page:
                yield {}
            for manga in mangas:
                details = manga.find("div", {"class": "bigor-manga"})
                ti = details.find("h3", {"class": "tt"}).find("a")
                if absolute and keyword.lower() not in ti["title"].lower():
                    continue
                with suppress(Exception):
                    latest_chapter = (
                        details.find("div", {"class": "list-chapter"})
                        .find("a")["href"]
                        .split("/")[-1]
                    )
                results[ti["title"]] = {
                    "domain": Manga18fx.domain,
                    "url": ti["href"].split("/")[-1],
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("img")["data-src"],
                    "page": page,
                }
            prev_page = mangas
            yield results
            page += 1

    def get_db():
        return Manga18fx.search_by_keyword("", False)
