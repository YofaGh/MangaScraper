from utils.models import Doujin
from user_agents import MOZILLA


class E_Hentai(Doujin):
    domain = "e-hentai.org"
    logo = "https://e-hentai.org/favicon.ico"
    headers = {"User-Agent": MOZILLA}
    is_coded = False

    def get_info(self, code):
        from contextlib import suppress

        response, _ = self.send_request(
            f"https://e-hentai.org/g/{code}", headers=self.headers
        )
        soup = self.get_html_parser(response.text)
        cover, title, pages, rating = 4 * [""]
        box = soup.find("div", {"class": "gm"})
        infos = {
            info.find("td").get_text(strip=True)[:-1]: info.find(
                "td", {"class": "gdt2"}
            ).get_text(strip=True)
            for info in box.find("div", {"id": "gdd"}).find_all("tr")
        }
        extras = {}
        with suppress(Exception):
            cover = (
                soup.find("div", {"id": "gd1"})
                .find("div")["style"]
                .split("url(")[1]
                .split(")")[0]
            )
        with suppress(Exception):
            title = box.find("h1").get_text(strip=True)
        with suppress(Exception):
            extras["Size"] = infos["File Size"]
        with suppress(Exception):
            pages = infos["Length"].replace(" pages", "")
        with suppress(Exception):
            rating = float(
                box.find("td", {"id": "rating_label"})
                .get_text(strip=True)
                .replace("Average:", "")
            )
        for bx in box.find("div", {"id": "taglist"}).find_all("tr"):
            with suppress(Exception):
                extras[bx.find("td").get_text(strip=True)] = [
                    link.get_text(strip=True) for link in bx.find_all("div")
                ]
        return {
            "Cover": cover,
            "Title": title,
            "Pages": pages,
            "Rating": rating,
            "Extras": extras,
            "Dates": {"Posted": f"{infos['Posted']}:00"},
        }

    def get_title(self, code):
        response, _ = self.send_request(
            f"https://e-hentai.org/g/{code}", headers=self.headers
        )
        soup = self.get_html_parser(response.text)
        title = soup.find("h1").get_text(strip=True)
        return title

    def get_images(self, code):
        response, session = self.send_request(f"https://e-hentai.org/g/{code}")
        self.headers = self.headers
        soup = self.get_html_parser(response.text)
        pages = [a["href"] for a in soup.find("div", {"id": "gdt"}).find_all("a")]
        images, save_names = [], []
        for i in range(len(pages)):
            response, session = self.send_request(pages[i], session=session)
            soup = self.get_html_parser(response.text)
            image = soup.find("img", {"id": "img"})["src"]
            images.append(image)
            save_names.append(f"{i + 1:03d}.{image.split('.')[-1]}")
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        page = 1
        last = ""
        session = None
        while True:
            response, session = self.send_request(
                f"https://e-hentai.org/?f_search={keyword}&next={last}",
                session=session,
                headers=self.headers,
            )
            if (
                "No unfiltered results found" in response.text
                or "No hits found" in response.text
            ):
                yield {}
            soup = self.get_html_parser(response.text)
            doujins = soup.find("table", {"class": "itg"}).find_all("tr")[1:]
            results = {}
            for doujin in doujins:
                if doujin.find("td", {"class": "itd"}):
                    continue
                ti = doujin.find("div", {"class": "glink"}).get_text(strip=True)
                if absolute and keyword.lower() not in ti.lower():
                    continue
                code = (
                    doujin.find("td", {"class": "gl3c glname"})
                    .find("a")["href"]
                    .replace("https://e-hentai.org/g/", "")[:-1]
                )
                thumbnail = doujin.find("img")
                thumbnail = (
                    thumbnail["data-src"]
                    if thumbnail.has_attr("data-src")
                    else thumbnail["src"]
                )
                results[ti] = {
                    "domain": self.domain,
                    "code": code,
                    "category": doujin.find("div", {"class": "cn"}).get_text(
                        strip=True
                    ),
                    "thumbnail": thumbnail,
                    "page": page,
                }
                last = code.split("/")[0]
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)
