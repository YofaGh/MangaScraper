from utils.models import Manga


class Manga68(Manga):
    domain = "manga68.com"
    logo = (
        "https://manga68.com/wp-content/uploads/2017/10/cropped-manga68-2-192x192.png"
    )

    def get_info(self, manga):
        from contextlib import suppress

        response, _ = self.send_request(f"https://manga68.com/manga/{manga}")
        soup = self.get_html_parser(response.text)
        cover, title, summary, rating, status = 5 * [""]
        extras = {}
        info_box = soup.find("div", {"class": "tab-summary"})
        with suppress(Exception):
            cover = info_box.find("img")["data-src"]
        with suppress(Exception):
            title = (
                soup.find("div", {"id": "manga-title"}).find("h1").contents[-1].strip()
            )
        with suppress(Exception):
            rating = float(
                info_box.find("div", {"class": "post-total-rating"})
                .find("span")
                .get_text(strip=True)
            )
        for box in soup.find("div", {"class": "post-content"}).find_all(
            "div", {"class": "post-content_item"}
        ):
            if "Rating" in box.get_text(strip=True) or "Comments" in box.get_text(
                strip=True
            ):
                continue
            elif "Summary" in box.get_text(strip=True):
                with suppress(Exception):
                    summary = box.find("p").get_text(strip=True)
            elif "Status" in box.get_text(strip=True):
                with suppress(Exception):
                    status = box.find("div", {"class": "summary-content"}).get_text(
                        strip=True
                    )
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
            "Summary": summary,
            "Rating": rating,
            "Status": status,
            "Extras": extras,
        }

    def get_chapters(self, manga):
        response, _ = self.send_request(
            f"https://manga68.com/manga/{manga}/ajax/chapters/", method="POST"
        )
        soup = self.get_html_parser(response.text)
        divs = soup.find_all("li", {"class": "wp-manga-chapter"})
        chapters_urls = [div.find("a")["href"].split("/")[-2] for div in divs[::-1]]
        chapters = [
            {"url": chapter_url, "name": self.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(self, manga, chapter):
        response, _ = self.send_request(
            f"https://manga68.com/manga/{manga}/{chapter['url']}/"
        )
        soup = self.get_html_parser(response.text)
        images = soup.find("div", {"class": "reading-content"}).find_all("img")
        images = [image["data-src"].strip() for image in images]
        return images, False

    def search_by_keyword(self, keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError

        page = 1
        session = None
        while True:
            try:
                response, session = self.send_request(
                    f"https://manga68.com/page/{page}/?s={keyword}&post_type=wp-manga",
                    session=session,
                )
            except HTTPError:
                yield {}
            if response.url == f"https://manga68.com?s={keyword}&post_type=wp-manga":
                yield {}
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "row c-tabs-item__content"})
            results = {}
            for manga in mangas:
                tilink = manga.find("div", {"class", "post-title"})
                if (
                    absolute
                    and keyword.lower() not in tilink.get_text(strip=True).lower()
                ):
                    continue
                latest_chapter, authors, artists, genres, status, release_date = (
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                )
                contents = manga.find_all("div", {"class": "post-content_item"})
                for content in contents:
                    with suppress(Exception):
                        if "Authors" in content.text:
                            authors = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Artists" in content.text:
                            artists = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Genres" in content.text:
                            genres = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Status" in content.text:
                            status = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Release" in content.text:
                            release_date = content.find("a").get_text(strip=True)
                with suppress(Exception):
                    latest_chapter = (
                        manga.find("span", {"class": "font-meta chapter"})
                        .find("a")["href"]
                        .split("/")[-2]
                    )
                results[tilink.get_text(strip=True)] = {
                    "domain": self.domain,
                    "url": tilink.find("a")["href"].split("/")[-2],
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("img")["data-src"],
                    "genres": genres,
                    "authors": authors,
                    "artists": artists,
                    "status": status,
                    "release_date": release_date,
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)
