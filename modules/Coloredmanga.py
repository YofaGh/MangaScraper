from utils.models import Manga


class Coloredmanga(Manga):
    domain = "coloredmanga.com"
    logo = "https://coloredmanga.com/wp-content/uploads/2022/09/cropped-000-192x192.png"

    def get_info(self, manga):
        from contextlib import suppress

        response, _ = self.send_request(f"https://coloredmanga.com/mangas/{manga}/")
        soup = self.get_html_parser(response.text)
        cover, title, alternative, rating, status = 5 * [""]
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
            "Alternative": alternative,
            "Rating": rating,
            "Status": status,
            "Extras": extras,
        }

    def get_chapters(self, manga):
        response, _ = self.send_request(f"https://coloredmanga.com/mangas/{manga}/")
        soup = self.get_html_parser(response.text)
        divs = soup.find_all("li", {"class": "wp-manga-chapter"})
        chapters_urls = [
            div.find("a")["href"].replace(
                f"https://coloredmanga.com/mangas/{manga}/", ""
            )[:-1]
            for div in divs[::-1]
        ]
        chapters = [
            {"url": chapter_url, "name": self.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(self, manga, chapter):
        response, _ = self.send_request(
            f"https://coloredmanga.com/mangas/{manga}/{chapter['url']}/"
        )
        soup = self.get_html_parser(response.text)
        images = soup.find("div", {"class": "reading-content"}).find_all("img")
        images = [image["src"].strip() for image in images]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1]}" for i in range(len(images))
        ]
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError

        page = 1
        session = None
        while True:
            try:
                response, session = self.send_request(
                    f"https://coloredmanga.com/page/{page}/?s={keyword}&post_type=wp-manga",
                    session=session,
                )
            except HTTPError:
                yield {}
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "row c-tabs-item__content"})
            results = {}
            for manga in mangas:
                tilink = manga.find("div", {"class", "post-title"})
                if absolute and keyword.lower() not in manga.find("a")["href"]:
                    continue
                (
                    latest_chapter,
                    thumbnail,
                    authors,
                    artists,
                    genres,
                    status,
                    release_date,
                ) = "", "", "", "", "", "", ""
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
                with suppress(Exception):
                    thumbnail = manga.find("img")["src"]
                results[tilink.get_text(strip=True)] = {
                    "domain": self.domain,
                    "url": tilink.find("a")["href"].replace(
                        "https://coloredmanga.com/mangas/", ""
                    )[:-1],
                    "latest_chapter": latest_chapter,
                    "thumbnail": thumbnail,
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

    @staticmethod
    def rename_chapter(chapter):
        beginner = "Chapter"
        if "volume" in chapter:
            beginner = "Volume"
        elif "number" in chapter:
            beginner = "Number"
        new_name = ""
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in "-._" and reached_number and new_name[-1] != ".":
                new_name += "."
        if not reached_number:
            return chapter
        new_name = new_name.rstrip(".")
        try:
            return f"{beginner} {int(new_name):03d}"
        except ValueError:
            return f"{beginner} {new_name.split('.', 1)[0].zfill(3)}.{new_name.split('.', 1)[1]}"
