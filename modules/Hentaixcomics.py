from utils.models import Doujin


class Hentaixcomics(Doujin):
    domain = "hentaixcomics.com"
    logo = "https://hentaixcomics.com/assets/img/favicon.ico"
    is_coded = False
    language_codes = {"us": "English", "jp": "Japanese", "cn": "Chinese"}

    def get_info(self, code):
        from contextlib import suppress

        response, _ = self.send_request(f"https://hentaixcomics.com/{code}/")
        soup = self.get_html_parser(response.text)
        cover, title, alternative, summary, pages = 5 * [""]
        info_box = soup.find("div", {"id": "info"})
        extras = {}
        with suppress(Exception):
            cover = soup.find("div", {"id": "cover"}).find("img")["data-src"]
        with suppress(Exception):
            title = info_box.find("h1").get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find("h4").get_text(strip=True)
        with suppress(Exception):
            extras["Uploaded"] = info_box.find("time").get_text(strip=True)
        with suppress(Exception):
            pages = (
                info_box.find_all(
                    lambda tag: tag.name == "div" and "pages" in tag.text
                )[-1]
                .get_text(strip=True)
                .split(" ")[0]
            )
        with suppress(Exception):
            summary = (
                soup.find("p", {"class": "grey tleft"})
                .get_text(strip=True)
                .replace("\n", "")
                .replace("\t", "")
                .replace("\r", "")
            )
        tag_box = soup.find("section", {"id": "tags"}).find_all(
            "div", {"class": "tag-container field-name"}
        )
        for box in tag_box:
            with suppress(Exception):
                extras[box.contents[0].strip().rstrip(":")] = [
                    link.contents[0].strip() for link in box.find_all("a")
                ]
        return {
            "Cover": cover,
            "Title": title,
            "Pages": pages,
            "Alternative": alternative,
            "Summary": summary,
            "Extras": extras,
        }

    def get_title(self, code):
        response, _ = self.send_request(f"https://hentaixcomics.com/{code}/")
        soup = self.get_html_parser(response.text)
        title = soup.find("div", {"id": "info"}).find("h1").get_text(strip=True)
        return title

    def get_images(self, code):
        import json

        response, _ = self.send_request(f"https://hentaixcomics.com/{code}/")
        soup = self.get_html_parser(response.text)
        images_raw = soup.find("textarea").get_text(strip=True)
        images = json.loads(images_raw)
        return images, False

    def search_by_keyword(self, keyword, absolute):
        page = 1
        prev_page = []
        session = None
        while True:
            response, session = self.send_request(
                f"https://hentaixcomics.com/search/?s={keyword}&page={page}",
                session=session,
            )
            soup = self.get_html_parser(response.text)
            if soup.find("span", {"class": "count"}).get_text(strip=True) == "(0)":
                yield {}
            doujins = soup.find_all("div", {"class": "gallery"})
            if prev_page == doujins:
                yield {}
            results = {}
            for doujin in doujins:
                if (
                    absolute
                    and keyword.lower() not in doujin.get_text(strip=True).lower()
                ):
                    continue
                results[doujin.get_text(strip=True)] = {
                    "domain": self.domain,
                    "code": doujin.find("a")["href"].split("/")[-2],
                    "thumbnail": doujin.find("img")["data-src"],
                    "language": self.language_codes[doujin.find("span")["class"][1]],
                    "page": page,
                }
            prev_page = doujins
            yield results
            page += 1

    def get_db(self):
        for category in ("manga", "doujinshi"):
            page = 1
            prev_page = []
            session = None
            while True:
                response, session = self.send_request(
                    f"https://hentaixcomics.com/s/{category}/page/{page}",
                    session=session,
                )
                soup = self.get_html_parser(response.text)
                if soup.find("span", {"class": "count"}).get_text(strip=True) == "(0)":
                    break
                doujins = soup.find_all("div", {"class": "gallery"})
                if prev_page == doujins:
                    break
                results = {}
                for doujin in doujins:
                    results[doujin.get_text(strip=True)] = {
                        "domain": self.domain,
                        "code": doujin.find("a")["href"].split("/")[-2],
                        "thumbnail": doujin.find("img")["data-src"],
                        "language": self.language_codes[
                            doujin.find("span")["class"][1]
                        ],
                        "category": category,
                        "page": page,
                    }
                prev_page = doujins
                yield results
                page += 1
        yield {}
