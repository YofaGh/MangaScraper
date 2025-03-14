from utils.models import Doujin
from user_agents import LEECH


class Simply_hentai(Doujin):
    domain = "simply-hentai.com"
    logo = "https://www.simply-hentai.com/images/logo.svg"
    headers = {"User-Agent": LEECH}
    is_coded = False

    def get_info(self, code):
        from contextlib import suppress
        from datetime import datetime

        response, _ = self.send_request(
            f"https://www.simply-hentai.com/{code}", headers=self.headers
        )
        soup = self.get_html_parser(response.text)
        cover, title, pages, uploaded = 4 * [""]
        info_box = soup.find("section", {"class": "album-info"})
        extras = {}
        with suppress(Exception):
            cover = info_box.find("img")["data-src"]
        with suppress(Exception):
            title = info_box.find("h1").get_text(strip=True)
        with suppress(Exception):
            extras["Views"] = (
                info_box.find("div", {"class": "row mb-2 align-items-center"})
                .find("div", {"class": "col-4"})
                .find("div")
                .get_text(strip=True)
            )
        with suppress(Exception):
            uploaded = (
                info_box.find("div", {"class": "row mb-2 align-items-center"})
                .find("div", {"class": "col-5"})
                .find("div")
                .get_text(strip=True)
            )
        with suppress(Exception):
            pages = (
                info_box.find("div", {"class": "col-12 col-lg-4"})
                .find_all("a")[-1]
                .get_text(strip=True)[11:-1]
            )
        attr, lis = None, []
        for child in (
            info_box.find_all("div", {"class": "col-12 col-sm-6 col-lg-4"})[1]
            .find("div", {"class": "data-wrapper"})
            .children
        ):
            if child.name == "div":
                if attr:
                    extras[attr] = lis
                attr = child.get_text(strip=True)
                lis = []
            else:
                lis.append(child.get_text(strip=True))
        extras[attr] = lis
        return {
            "Cover": cover,
            "Title": title,
            "Pages": pages,
            "Extras": extras,
            "Dates": {
                "Uploaded": datetime.strptime(uploaded, "%m/%d/%Y").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            },
        }

    def get_title(self, code):
        response, _ = self.send_request(
            f"https://www.simply-hentai.com/{code}", headers=self.headers
        )
        soup = self.get_html_parser(response.text)
        title = (
            soup.find("section", {"class", "album-info"})
            .find("h1")
            .get_text(strip=True)
        )
        return title

    def get_images(self, code):
        import json

        response, _ = self.send_request(
            f"https://www.simply-hentai.com/{code}/all-pages",
            headers=self.headers,
        )
        soup = self.get_html_parser(response.text)
        script = soup.find("script", {"id": "__NEXT_DATA__"}).get_text(strip=True)
        data_raw = json.loads(script)
        images = [
            image["sizes"]["full"]
            for image in data_raw["props"]["pageProps"]["data"]["pages"]
        ]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1].split('?')[0]}"
            for i in range(len(images))
        ]
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        page = 1
        session = None
        while True:
            response, session = self.send_request(
                f"https://api.simply-hentai.com/v3/search/complex?filter[class_name][0]=Manga&query={keyword}&page={page}",
                session=session,
                headers=self.headers,
            )
            datas = response.json()["data"]
            if not datas:
                yield {}
            results = {}
            for data in datas:
                doujin = data["object"]
                if absolute and keyword.lower() not in doujin["title"].lower():
                    continue
                results[doujin["title"]] = {
                    "domain": self.domain,
                    "code": f"{doujin['series']['slug']}/{doujin['slug']}",
                    "thumbnail": doujin["preview"]["sizes"]["thumb"],
                    "page": page,
                }
            page += 1
            yield results

    def get_db(self):
        page = 1
        prev_page = None
        session = None
        while True:
            response, session = self.send_request(
                f"https://www.simply-hentai.com/2-mangas/page-{page}",
                session=session,
                headers=self.headers,
            )
            soup = self.get_html_parser(response.text)
            results = {}
            divs = soup.find_all("div", {"class", "col-6 col-lg-3"})
            if divs == prev_page:
                yield {}
            for div in divs:
                doujin = div.find("div", {"class", "info"})
                tilink = doujin.find("a")
                language = doujin.find("a", {"class", "is-trigger ism-trigger"})[
                    "href"
                ].split("/")[-1]
                number_of_pages = doujin.find(
                    "div", {"class", "col-8 text-right count-col"}
                ).get_text(strip=True)
                results[tilink.get_text(strip=True)] = {
                    "domain": self.domain,
                    "code": tilink["href"][1:],
                    "language": language,
                    "number_of_pages": number_of_pages,
                    "page": page,
                }
            page += 1
            yield results
            prev_page = divs
