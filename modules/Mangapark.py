from utils.models import Manga


class Mangapark(Manga):
    domain = "mangapark.to"
    logo = "https://mangapark.to/public-assets/img/favicon.ico"

    def get_info(self, manga):
        from contextlib import suppress

        manga = manga.split("-")[0] if "-" in manga else manga
        response, _ = self.send_request(f"https://mangapark.to/title/{manga}")
        soup = self.get_html_parser(response.text)
        cover, title, alternative, summary, status, rating = 6 * [""]
        info_box = soup.find("div", {"class": "flex flex-col md:flex-row"})
        extras = {}
        with suppress(Exception):
            cover = info_box.find("img")["src"]
        with suppress(Exception):
            title = info_box.find("h3").get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find("div", {"q:key": "tz_2"}).get_text(strip=True)
        with suppress(Exception):
            summary = info_box.find(
                "div", {"class": "limit-html prose lg:prose-lg"}
            ).get_text(strip=True)
        with suppress(Exception):
            status = info_box.find("span", {"q:key": "Yn_5"}).get_text(strip=True)
        with suppress(Exception):
            extras["Genres"] = [
                a.get_text(strip=True)
                for a in info_box.find_all("span", {"q:key": "kd_0"})
            ]
        with suppress(Exception):
            rating = float(
                info_box.find("span", {"q:key": "lt_0"}).get_text(strip=True)
            )
        return {
            "Cover": cover,
            "Title": title,
            "Alternative": alternative,
            "Summary": summary,
            "Status": status,
            "Rating": rating,
            "Extras": extras,
        }

    def get_chapters(self, manga):
        import json

        response, _ = self.send_request(f"https://mangapark.to/title/{manga}")
        soup = self.get_html_parser(response.text)
        script = soup.find("script", {"type": "qwik/json"}).text
        data = json.loads(script)["objs"]
        chapters = [
            {
                "url": item.split("/")[-1],
                "name": self.rename_chapter(str(data[i - 1])),
            }
            for i, item in enumerate(data)
            if isinstance(item, str) and f"{manga}/" in item
        ]
        return chapters

    def get_images(self, manga, chapter):
        import json

        response, _ = self.send_request(
            f"https://mangapark.to/title/{manga}/{chapter['url']}"
        )
        soup = self.get_html_parser(response.text)
        script = soup.find("script", {"type": "qwik/json"})
        data = json.loads(script.text)["objs"]
        images = [item for item in data if isinstance(item, str) and "/comic/" in item]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1]}" for i in range(len(images))
        ]
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        from contextlib import suppress

        page = 1
        session = None
        while True:
            response, session = self.send_request(
                f"https://mangapark.to/search?word={keyword}&page={page}",
                session=session,
            )
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all(
                "div", {"class": "flex border-b border-b-base-200 pb-5"}
            )
            if not mangas:
                yield {}
            results = {}
            for manga in mangas:
                name = manga.find("h3").get_text(strip=True)
                url = manga.find("h3").find("a")["href"].split("/")[-1]
                authors, alternatives, genres, latest_chapter = "", "", "", ""
                with suppress(Exception):
                    authors = ", ".join(
                        manga.find("div", {"q:key": "6N_0"})
                        .get_text(strip=True)
                        .split("/")
                    )
                with suppress(Exception):
                    alternatives = ", ".join(
                        manga.find("div", {"q:key": "lA_0"})
                        .get_text(strip=True)
                        .split("/")
                    )
                with suppress(Exception):
                    genres = ", ".join(
                        manga.find("div", {"q:key": "HB_9"})
                        .get_text(strip=True)
                        .split(",")
                    )
                with suppress(Exception):
                    latest_chapter = (
                        manga.find("div", {"q:key": "R7_8"})
                        .find("a")["href"]
                        .split("/")[-1]
                    )
                if absolute and keyword.lower() not in name.lower():
                    continue
                results[name] = {
                    "domain": self.domain,
                    "url": url,
                    "thumbnail": manga.find("img")["src"],
                    "alternatives": alternatives,
                    "authors": authors,
                    "genres": genres,
                    "latest_chapter": latest_chapter,
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)
