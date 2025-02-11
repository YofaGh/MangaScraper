from utils.models import Doujin


class Hentaifox(Doujin):
    domain = "hentaifox.com"
    logo = "https://hentaifox.com/images/logo.png"
    image_formats = {"j": "jpg", "p": "png", "b": "bmp", "g": "gif", "w": "webp"}

    def get_info(self, code):
        from contextlib import suppress

        response, _ = self.send_request(f"https://hentaifox.com/gallery/{code}")
        soup = self.get_html_parser(response.text)
        cover, title, pages = 3 * [""]
        info_box = soup.find("div", {"class": "info"})
        extras = {}
        with suppress(Exception):
            cover = soup.find("div", {"class": "cover"}).find("img")["src"]
        with suppress(Exception):
            title = info_box.find("h1").get_text(strip=True)
        with suppress(Exception):
            extras["Posted"] = (
                info_box.find(lambda tag: "Posted" in tag.text)
                .get_text(strip=True)
                .replace("Posted: ", "")
            )
        with suppress(Exception):
            pages = (
                info_box.find(lambda tag: "Pages" in tag.text)
                .get_text(strip=True)
                .replace("Pages: ", "")
            )
        for box in info_box.find_all(
            lambda tag: tag.name == "ul" and "g_buttons" not in tag.get("class")
        ):
            with suppress(Exception):
                extras[box.find("span").get_text(strip=True)[:-1]] = [
                    link.contents[0].strip() for link in box.find_all("a")
                ]
        return {"Cover": cover, "Title": title, "Pages": pages, "Extras": extras}

    def get_title(self, code):
        response, _ = self.send_request(f"https://hentaifox.com/gallery/{code}")
        soup = self.get_html_parser(response.text)
        title = soup.find("div", {"class", "info"}).find("h1").get_text(strip=True)
        return title

    def get_images(self, code):
        import json

        response, _ = self.send_request(f"https://hentaifox.com/gallery/{code}")
        soup = self.get_html_parser(response.text)
        path = (
            soup.find("div", {"class": "gallery_thumb"})
            .find("img")["data-src"]
            .rsplit("/", 1)[0]
        )
        script = soup.find(
            lambda tag: tag.name == "script" and "var g_th" in tag.text
        ).text
        images = json.loads(script.replace("var g_th = $.parseJSON('", "")[:-4])
        images = [
            f"{path}/{image}.{self.image_formats[images[image][0]]}" for image in images
        ]
        return images, False

    def search_by_keyword(self, keyword, absolute):
        from requests.exceptions import HTTPError

        page = 1
        session = None
        while True:
            try:
                response, session = self.send_request(
                    f"https://hentaifox.com/search/?q={keyword}&page={page}",
                    session=session,
                )
            except HTTPError:
                yield {}
            soup = self.get_html_parser(response.text)
            doujins = soup.find_all("div", {"class": "thumb"})
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                caption = doujin.find("div", {"class": "caption"})
                ti = caption.find("a").get_text()
                if absolute and keyword.lower() not in ti.lower():
                    continue
                results[ti] = {
                    "domain": self.domain,
                    "code": caption.find("a")["href"].split("/")[-2],
                    "category": doujin.find("a", {"class": "t_cat"}).get_text(),
                    "thumbnail": doujin.find("img")["src"],
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        from requests.exceptions import HTTPError

        response, session = self.send_request("https://hentaifox.com/categories/")
        soup = self.get_html_parser(response.text)
        categories = soup.find("div", {"class": "list_tags"}).find_all("a")
        categories = [a["href"] for a in categories]
        for category in categories:
            page = 1
            while True:
                try:
                    response, session = self.send_request(
                        f"https://hentaifox.com{category}pag/{page}/", session=session
                    )
                except HTTPError:
                    break
                soup = self.get_html_parser(response.text)
                doujins = soup.find_all("div", {"class": "thumb"})
                if not doujins:
                    break
                results = {}
                for doujin in doujins:
                    caption = doujin.find("div", {"class": "caption"})
                    ti = caption.find("a").get_text()
                    results[ti] = {
                        "domain": self.domain,
                        "code": caption.find("a")["href"].split("/")[-2],
                        "category": doujin.find("a", {"class": "t_cat"}).get_text(),
                    }
                yield results
                page += 1
        yield {}
