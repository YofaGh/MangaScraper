from utils.models import Manga
from user_agents import LEECH


class Constellarcomic(Manga):
    domain = "constellarcomic.com"
    logo = "https://constellarcomic.com/wp-content/uploads/2022/11/Constellar-Logo-Rounded-000.png"
    headers = {"User-Agent": LEECH}

    def get_info(self, manga):
        from contextlib import suppress

        response, _ = self.send_request(
            f"https://constellarcomic.com/manga/{manga}/",
            headers=self.headers,
        )
        soup = self.get_html_parser(response.text)
        cover, title, alternative, summary, rating, status = 6 * [""]
        info_box = soup.find("div", {"class": "main-info"})
        extras = {}
        with suppress(Exception):
            cover = info_box.find("img", {"class": "attachment- size- wp-post-image"})[
                "src"
            ]
        with suppress(Exception):
            title = info_box.find("h1", {"class": "entry-title"}).get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find("div", {"class": "desktop-titles"}).get_text(
                strip=True
            )
        with suppress(Exception):
            summary = info_box.find(
                "div", {"class": "entry-content entry-content-single"}
            ).get_text(strip=True)
        with suppress(Exception):
            rating = (
                float(info_box.find("div", {"class": "numscore"}).get_text(strip=True))
                / 2
            )
        with suppress(Exception):
            status = info_box.find("div", {"class": "status"}).get_text(strip=True)
        for box in info_box.find("div", {"class": "tsinfo bixbox"}).find_all(
            "div", {"class": "imptdt"}
        ):
            with suppress(Exception):
                extras[box.contents[0].strip()] = (
                    box.find("i").get_text(strip=True)
                    if box.find("i")
                    else box.find("a").get_text(strip=True)
                )
        with suppress(Exception):
            extras["Genres"] = [
                a.get_text(strip=True)
                for a in info_box.find("div", {"class": "wd-full"}).find_all("a")
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
        response, _ = self.send_request(
            f"https://constellarcomic.com/manga/{manga}/",
            headers=self.headers,
        )
        soup = self.get_html_parser(response.text)
        links = soup.find("div", {"id": "chapterlist"}).find_all("a")
        chapters_urls = [
            link["href"].split("/")[-2].replace(f"{manga}-", "") for link in links[::-1]
        ]
        chapters = [
            {"url": chapter_url, "name": self.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(self, manga, chapter):
        import json

        chapter_url = chapter["url"]
        if f"{manga}-" in chapter_url:
            chapter_url = chapter_url.replace(f"{manga}-", "")
        response, _ = self.send_request(
            f"https://constellarcomic.com/{manga}-{chapter_url}/",
            headers=self.headers,
        )
        soup = self.get_html_parser(response.text)
        script = soup.find(
            lambda tag: tag.name == "script" and "NO IMAGE YET" in tag.text
        )
        images = json.loads(
            script.get_text(strip=True).replace("ts_rea_der_._run(", "")[:-2]
        )
        images = images["sources"][0]["images"]
        return images, False

    def search_by_keyword(self, keyword, absolute):
        from contextlib import suppress

        page = 1
        session = None
        while True:
            response, session = self.send_request(
                f"https://constellarcomic.com/page/{page}/?s={keyword}",
                session=session,
                headers=self.headers,
            )
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "bs swiper-slide"})
            if (
                not mangas
                or response.url == f"https://constellarcomic.com/?s={keyword}"
            ):
                yield {}
            results = {}
            for manga in mangas:
                ti = manga.find("a")
                if absolute and keyword.lower() not in ti["title"].lower():
                    continue
                status = ""
                with suppress(Exception):
                    status = ti.find("i").get_text(strip=True)
                results[ti["title"]] = {
                    "domain": self.domain,
                    "url": ti["href"].split("/")[-2],
                    "thumbnail": manga.find("img")["src"],
                    "status": status,
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)
