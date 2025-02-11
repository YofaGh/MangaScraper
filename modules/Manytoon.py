from utils.models import Manga


class Manytoon(Manga):
    domain = "manytoon.com"
    logo = "https://manytoon.com/favicon.ico"

    def get_info(manga):
        from contextlib import suppress

        response, _ = Manytoon.send_request(f"https://manytoon.com/comic/{manga}")
        soup = Manytoon.get_html_parser(response.text)
        cover, title, alternative, summary, rating, status = 6 * [""]
        extras = {}
        info_box = soup.find("div", {"class": "tab-summary"})
        with suppress(Exception):
            cover = info_box.find("img")["src"]
        with suppress(Exception):
            title = (
                soup.find("div", {"class": "post-title"})
                .find("h1")
                .contents[-1]
                .strip()
            )
        with suppress(Exception):
            summary = (
                soup.find("div", {"class": "summary__content"})
                .find("p")
                .contents[-1]
                .strip()
            )
        with suppress(Exception):
            rating = float(
                info_box.find(
                    "span", {"class": "score font-meta total_votes"}
                ).get_text(strip=True)
            )
        with suppress(Exception):
            extras["Release"] = (
                info_box.find("div", {"class": "post-status"})
                .find_all("div", {"class": "summary-content"})[0]
                .get_text(strip=True)
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
        response, session = Manytoon.send_request(f"https://manytoon.com/comic/{manga}")
        soup = Manytoon.get_html_parser(response.text)
        post_id = soup.find("a", {"class": "wp-manga-action-button"})["data-post"]
        data = {"action": "ajax_chap", "post_id": int(post_id)}
        response, _ = Manytoon.send_request(
            "https://manytoon.com/wp-admin/admin-ajax.php",
            method="POST",
            session=session,
            data=data,
        )
        soup = Manytoon.get_html_parser(response.text)
        lis = soup.find_all("li", {"class": "wp-manga-chapter"})
        chapters_urls = [li.find("a")["href"].split("/")[-2] for li in lis[::-1]]
        chapters = [
            {"url": chapter_url, "name": Manytoon.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(manga, chapter):
        response, _ = Manytoon.send_request(
            f"https://manytoon.com/comic/{manga}/{chapter['url']}/"
        )
        soup = Manytoon.get_html_parser(response.text)
        images = soup.find("div", {"class": "reading-content"}).find_all("img")
        images = [image["src"].strip() for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError

        page = 1
        session = None
        while True:
            try:
                response, session = Manytoon.send_request(
                    f"https://manytoon.com/page/{page}/?s={keyword}&post_type=wp-manga",
                    session=session,
                )
            except HTTPError:
                yield {}
            soup = Manytoon.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "col-6 col-md-3 badge-pos-1"})
            results = {}
            for manga in mangas:
                ti = (
                    manga.find("div", {"class": "post-title"})
                    .find("a")
                    .get_text(strip=True)
                )
                if absolute and keyword.lower() not in ti.lower():
                    continue
                link = (
                    manga.find("div", {"class": "post-title"})
                    .find("a")["href"]
                    .split("/")[-2]
                )
                latest_chapter = ""
                with suppress(Exception):
                    latest_chapter = (
                        manga.find("span", {"class": "chapter font-meta"})
                        .find("a")["href"]
                        .split("/")[-2]
                    )
                results[ti] = {
                    "domain": Manytoon.domain,
                    "url": link,
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("img")["src"],
                    "page": page,
                }
            yield results
            page += 1

    def get_db():
        return Manytoon.search_by_keyword("", False)
