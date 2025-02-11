from utils.models import Manga


class Bato(Manga):
    domain = "bato.to"
    logo = "https://bato.to/public-assets/img/favicon.ico"

    def get_info(self, manga):
        from contextlib import suppress

        response, _ = self.send_request(f"https://bato.to/title/{manga}")
        soup = self.get_html_parser(response.text)
        cover, title, alternative, summary, rating, status = 6 * [""]
        info_box = soup.find("div", {"class": "flex flex-col md:flex-row"})
        extras = {}
        with suppress(Exception):
            cover = info_box.find("img")["src"]
        with suppress(Exception):
            title = info_box.find("h3").get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find(
                "div", {"class": "mt-1 text-xs md:text-base opacity-80"}
            ).get_text(strip=True)
        with suppress(Exception):
            summary = (
                info_box.find("div", {"class": "relative w-full"})
                .find("astro-island")
                .get_text(strip=True)
            )
        with suppress(Exception):
            rating = (
                float(
                    soup.find(
                        "span",
                        {
                            "class": "font-black text-[2.0rem] md:text-[2.5rem] text-yellow-500"
                        },
                    ).get_text(strip=True)
                )
                / 2
            )
        with suppress(Exception):
            status = (
                info_box.find(lambda tag: "Status" in tag.text)
                .find("i")
                .get_text(strip=True)
            )
        with suppress(Exception):
            extras["By"] = [
                a.get_text(strip=True)
                for a in info_box.find(
                    "div", {"class": "mt-2 text-sm md:text-base opacity-80"}
                ).find_all("a")
            ]
        with suppress(Exception):
            extras["Genres"] = [
                f.find("span").get_text(strip=True)
                for f in info_box.find(
                    "div", {"class": "flex items-center flex-wrap"}
                ).find_all("span", recursive=False)
            ]
        return {
            "Cover": cover,
            "Title": title,
            "Alternative": alternative,
            "Summary": summary,
            "Rating": rating,
            "Status": status,
            "Extras": extras,
        }

    def get_chapters(self, manga):
        response, _ = self.send_request(f"https://bato.to/title/{manga}")
        soup = self.get_html_parser(response.text)
        links = soup.find("div", {"class": "group flex flex-col-reverse"}).find_all(
            "a", {"class": "link-hover link-primary visited:text-accent"}
        )
        chapters_urls = [link["href"].split("/")[-1] for link in links]
        chapters = [
            {"url": chapter_url, "name": self.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(self, manga, chapter):
        import json

        response, _ = self.send_request(
            f"https://bato.to/title/{manga}/{chapter['url']}"
        )
        soup = self.get_html_parser(response.text)
        props = soup.find(
            lambda tag: tag.name == "astro-island" and "imageFiles" in tag.get("props")
        )["props"]
        images = json.loads(props)["imageFiles"][1]
        images = [ima[1] for ima in json.loads(images)]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1].split('?')[0]}"
            for i in range(len(images))
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
                    f"https://bato.to/v3x-search?word={keyword}&page={page}",
                    session=session,
                )
            except HTTPError:
                yield {}
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all(
                "div", {"class": "flex border-b border-b-base-200 pb-5"}
            )
            if not mangas:
                yield {}
            results = {}
            for index, manga in enumerate(mangas):
                ti = manga.find("h3").find("a")
                if absolute and keyword.lower() not in ti.get_text(strip=True).lower():
                    continue
                alias, genres, latest_chapter = "", "", ""
                with suppress(Exception):
                    alias = manga.find(
                        "div", {"data-hk": f"0-0-3-{index}-4-0"}
                    ).get_text(strip=True)
                with suppress(Exception):
                    genres = manga.find(
                        "div", {"data-hk": f"0-0-3-{index}-6-0"}
                    ).get_text(strip=True)
                with suppress(Exception):
                    latest_chapter = (
                        manga.find("div", {"data-hk": f"0-0-3-{index}-7-1-0-0"})
                        .find("a")["href"]
                        .split("/")[-1]
                    )
                results[ti.get_text(strip=True)] = {
                    "domain": self.domain,
                    "url": ti["href"].replace("/title/", ""),
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("img")["src"],
                    "genres": genres,
                    "alias": alias,
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)

    @staticmethod
    def rename_chapter(chapter):
        chap = chapter.split("-", 1)[1] if "-" in chapter else chapter
        new_name = ""
        reached_number = False
        for ch in chap:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in "-." and reached_number and new_name[-1] != ".":
                new_name += "."
        if not reached_number:
            return chap
        new_name = new_name.rstrip(".")
        try:
            return f"Chapter {int(new_name):03d}"
        except ValueError:
            return f"Chapter {new_name.split('.', 1)[0].zfill(3)}.{new_name.split('.', 1)[1]}"
