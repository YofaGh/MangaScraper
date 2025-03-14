from utils.models import Manga


class Vyvymanga(Manga):
    domain = "vyvymanga.net"
    logo = "https://vyvymanga.net/web/img/icon.png"

    def get_info(self, manga):
        from contextlib import suppress

        response, _ = self.send_request(f"https://vyvymanga.net/manga/{manga}")
        box = self.get_html_parser(response.text).find("div", {"class": "div-manga"})
        cover, title, alternative, summary, rating, status, authors, view, genres = (
            9 * [""]
        )
        bbox = box.find("div", {"class": "col-md-7"})
        with suppress(Exception):
            cover = box.find("img")["src"]
        with suppress(Exception):
            title = box.find("h1", {"class": "title"}).get_text(strip=True)
        with suppress(Exception):
            alternative = (
                box.find("div", {"class": "col-md-7"}).find("p").get_text(strip=True)
            )
        with suppress(Exception):
            summary = (
                box.find("div", {"class": "summary"})
                .find("p", {"class": "content"})
                .get_text(strip=True)
            )
        with suppress(Exception):
            authors = [
                a.get_text(strip=True)
                for a in bbox.find(
                    lambda tag: tag.name == "p" and "Authors" in tag.text
                ).find_all("a")
            ]
        with suppress(Exception):
            status = (
                bbox.find(lambda tag: tag.name == "p" and "Status" in tag.text)
                .contents[-1]
                .get_text(strip=True)
            )
        with suppress(Exception):
            view = (
                bbox.find(lambda tag: tag.name == "p" and "View" in tag.text)
                .contents[-1]
                .get_text(strip=True)
            )
        with suppress(Exception):
            genres = [
                a.get_text(strip=True)
                for a in bbox.find(
                    lambda tag: tag.name == "p" and "Genres" in tag.text
                ).find_all("a")
            ]
        with suppress(Exception):
            rating = (
                float(
                    bbox.find(lambda tag: tag.name == "p" and "Rating" in tag.text)
                    .contents[-1]
                    .split("/")[0]
                    .strip()
                )
                / 2
            )
        return {
            "Cover": cover,
            "Title": title,
            "Alternative": alternative,
            "Summary": summary,
            "Rating": rating,
            "Status": status,
            "Extras": {"Authors": authors, "View": view, "Genres": genres},
        }

    def get_chapters(self, manga):
        response, _ = self.send_request(f"https://vyvymanga.net/manga/{manga}")
        soup = self.get_html_parser(response.text)
        aas = soup.find_all(
            "a", {"class": "list-group-item list-group-item-action list-chapter"}
        )
        chapters = [
            {
                "url": aa["href"],
                "name": aa.find("span").get_text(strip=True).replace(":", "_"),
            }
            for aa in aas[::-1]
        ]
        return chapters

    def get_images(self, manga, chapter):
        response, _ = self.send_request(chapter["url"])
        soup = self.get_html_parser(response.text)
        images = soup.find("div", {"class": "vview carousel-inner"}).find_all("img")
        images = [image["data-src"] for image in images]
        save_names = [f"{i + 1:03d}" for i in range(len(images))]
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        from contextlib import suppress

        page = 1
        session = None
        while True:
            response, session = self.send_request(
                f"https://vyvymanga.net/search?q={keyword}&page={page}", session=session
            )
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "comic-item"})
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find("div", {"class": "comic-title"}).get_text(strip=True)
                if absolute and keyword.lower() not in ti.lower():
                    continue
                latest_chapter, status = "", "On Going"
                with suppress(Exception):
                    latest_chapter = manga.find(
                        "span", {"class": "tray-item"}
                    ).get_text(strip=True)
                with suppress(Exception):
                    if manga.find("span", {"class": "comic-completed"}):
                        status = "Completed"
                results[ti] = {
                    "domain": self.domain,
                    "url": manga.find("a")["href"].split("/")[-1],
                    "status": status,
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("div", {"class": "comic-image"})[
                        "data-background-image"
                    ],
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)

    @classmethod
    def download_image(cls, url, image_name, session=None, verify=None):
        try:
            response, _ = cls.send_request(
                url, session=session, headers=cls.download_images_headers, verify=verify
            )
            image_format = (
                cls.headers["Content-Disposition"].split(".")[-1].replace('"', "")
            )
            saved_path = f"{image_name}.{image_format}"
            with open(saved_path, "wb") as image:
                image.write(response.content)
                return saved_path
        except Exception:
            return None
