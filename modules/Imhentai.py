from utils.models import Doujin


class Imhentai(Doujin):
    domain = "imhentai.xxx"
    logo = "https://imhentai.xxx/images/logo.png"
    image_formats = {"j": "jpg", "p": "png", "b": "bmp", "g": "gif", "w": "webp"}

    def get_info(self, code):
        from contextlib import suppress

        response, _ = self.send_request(f"https://imhentai.xxx/gallery/{code}")
        soup = self.get_html_parser(response.text)
        cover, title, alternative, pages = 4 * [""]
        extras = {}
        with suppress(Exception):
            cover = soup.find("div", {"class": "col-md-4 col left_cover"}).find("img")[
                "data-src"
            ]
        with suppress(Exception):
            title = soup.find("h1").get_text(strip=True)
        with suppress(Exception):
            alternative = soup.find("p", {"class": "subtitle"}).get_text(strip=True)
        with suppress(Exception):
            pages = (
                soup.find(lambda tag: tag.name == "li" and "Pages" in tag.text)
                .get_text(strip=True)
                .replace("Pages:", "")
            )
        tag_box = soup.find("ul", {"class": "galleries_info"}).find_all("li")
        for box in tag_box:
            if "Pages" not in box.text:
                with suppress(Exception):
                    extras[box.find("span").get_text(strip=True)[:-1]] = [
                        link.contents[0].strip() for link in box.find_all("a")
                    ]
        return {
            "Cover": cover,
            "Title": title,
            "Pages": pages,
            "Alternative": alternative,
            "Extras": extras,
        }

    def get_title(self, code):
        response, _ = self.send_request(f"https://imhentai.xxx/gallery/{code}")
        soup = self.get_html_parser(response.text)
        title = (
            soup.find("div", {"class", "col-md-7 col-sm-7 col-lg-8 right_details"})
            .find("h1")
            .get_text(strip=True)
        )
        return title

    def get_images(self, code):
        import json

        response, _ = self.send_request(f"https://imhentai.xxx/gallery/{code}")
        soup = self.get_html_parser(response.text)
        path = (
            soup.find("div", {"id": "append_thumbs"})
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
                    f"https://imhentai.xxx/search/?key={keyword}&page={page}",
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
                    "category": doujin.find("a", {"class": "thumb_cat"}).get_text(),
                    "thumbnail": doujin.find("div", {"class": "inner_thumb"}).find(
                        "img"
                    )["data-src"],
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)
