from utils.models import Manga


class Hentaixcomic(Manga):
    domain = "hentaixcomic.com"
    logo = "https://hentaixcomic.com/wp-content/uploads/2020/07/cropped-Pg_00-1-192x192.jpg"

    def get_info(self, manga):
        from contextlib import suppress

        response, _ = self.send_request(f"https://hentaixcomic.com/manga/{manga}")
        soup = self.get_html_parser(response.text)
        cover, title, rating, status = 4 * [""]
        extras = {}
        info_box = soup.find("div", {"class": "tab-summary"})
        with suppress(Exception):
            cover = info_box.find("img")["src"]
        with suppress(Exception):
            title = (
                soup.find("div", {"class": "post-title"})
                .find("h1")
                .get_text(strip=True)
            )
        with suppress(Exception):
            rating = float(
                info_box.find("div", {"class": "post-total-rating"})
                .find("span")
                .get_text(strip=True)
            )
        with suppress(Exception):
            status = (
                info_box.find("div", {"class": "post-status"})
                .find("div", {"class": "summary-content"})
                .get_text(strip=True)
            )
        for box in soup.find("div", {"class": "post-content"}).find_all(
            "div", {"class": "post-content_item"}
        ):
            if "Rating" in box.get_text(strip=True):
                continue
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
            "Rating": rating,
            "Status": status,
            "Extras": extras,
        }

    def get_chapters(self, manga):
        session = Hentaixcomic.create_session()
        response, session = self.send_request(f"https://hentaixcomic.com/manga/{manga}")
        soup = self.get_html_parser(response.text)
        manga_id = soup.find("a", {"class": "wp-manga-action-button"})["data-post"]
        self.headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data = f"action=manga_get_chapters&manga={manga_id}"
        response, session = self.send_request(
            "https://hentaixcomic.com/wp-admin/admin-ajax.php",
            method="POST",
            session=session,
            data=data,
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
            f"https://hentaixcomic.com/manga/{manga}/{chapter['url']}"
        )
        soup = self.get_html_parser(response.text)
        images = soup.find("div", {"class": "reading-content"}).find_all("img")
        images = [image["src"].strip() for image in images]
        return images, False

    def search_by_keyword(self, keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError

        page = 1
        session = None
        while True:
            try:
                response, session = self.send_request(
                    f"https://hentaixcomic.com/page/{page}/?s={keyword}&post_type=wp-manga",
                    session=session,
                )
            except HTTPError:
                yield {}
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "row c-tabs-item__content"})
            results = {}
            for manga in mangas:
                ti = manga.find("div", {"class": "tab-thumb c-image-hover"}).find("a")[
                    "title"
                ]
                if absolute and keyword.lower() not in ti.lower():
                    continue
                link = (
                    manga.find("div", {"class": "tab-thumb c-image-hover"})
                    .find("a")["href"]
                    .split("/")[-2]
                )
                latest_chapter, genres, authors, status, release_date = (
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
                            release_date = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                with suppress(Exception):
                    latest_chapter = (
                        manga.find("span", {"class": "font-meta chapter"})
                        .find("a")["href"]
                        .split("/")[-2]
                    )
                results[ti] = {
                    "domain": self.domain,
                    "url": link,
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("img")["src"],
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
