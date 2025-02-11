from utils.models import Doujin


class _9hentai(Doujin):
    domain = "9hentai.com"
    logo = "https://9hentai.com/images/logo.png"

    def get_info(self, code):
        from contextlib import suppress

        response, _ = self.send_request(f"https://9hentai.com/g/{code}")
        soup = self.get_html_parser(response.text)
        cover, title, alternative, pages, uploaded = 5 * [""]
        info_box = soup.find("div", {"id": "info"})
        extras = {}
        with suppress(Exception):
            cover = soup.find("div", {"id": "cover"}).find("v-lazy-image")["src"]
        with suppress(Exception):
            title = info_box.find("h1").get_text(strip=True)
        with suppress(Exception):
            alternative = info_box.find("h2").get_text(strip=True)
        with suppress(Exception):
            extras["Uploaded"] = info_box.find("time").get_text(strip=True)
        with suppress(Exception):
            pages = (
                info_box.find(lambda tag: "pages" in tag.text)
                .get_text(strip=True)
                .replace(" pages", "")
            )
        tag_box = soup.find("section", {"id": "tags"}).find_all(
            "div", {"class": "tag-container field-name"}
        )
        for box in tag_box:
            with suppress(Exception):
                extras[box.contents[0].strip()[:-1]] = [
                    link.get_text(strip=True) for link in box.find_all("a")
                ]
        return {
            "Cover": cover,
            "Title": title,
            "Pages": pages,
            "Alternative": alternative,
            "Extras": extras,
        }

    def get_title(self, code):
        response, _ = self.send_request(
            "https://9hentai.com/api/getBookByID", method="POST", json={"id": code}
        )
        return response.json()["results"]["title"]

    def get_images(self, code):
        response, _ = self.send_request(
            "https://9hentai.com/api/getBookByID", method="POST", json={"id": code}
        )
        response = response.json()
        image_server = response["results"]["image_server"]
        images = [
            f"{image_server}{code}/{i + 1}.jpg"
            for i in range(response["results"]["total_page"])
        ]
        return images, False

    def search_by_keyword(self, keyword, absolute):
        json = {
            "search": {
                "text": keyword,
                "page": 0,
                "sort": 3 if keyword else 4,
                "pages": {"range": [0, 2000]},
                "tag": {
                    "text": "",
                    "type": 1,
                    "tags": [],
                    "items": {"included": [], "excluded": []},
                },
            }
        }
        session = None
        while True:
            response, session = self.send_request(
                "https://9hentai.com/api/getBook",
                method="POST",
                session=session,
                json=json,
            )
            doujins = response.json()["results"]
            if not doujins:
                yield {}
            results = {}
            for doujin in doujins:
                if absolute and keyword.lower() not in doujin["title"].lower():
                    continue
                results[doujin["title"]] = {
                    "domain": self.domain,
                    "code": doujin["id"],
                    "thumbnail": f"{doujin['image_server']}{doujin['id']}/cover-small.jpg",
                    "tags": ", ".join([tag["name"] for tag in doujin["tags"]]),
                    "page": json["search"]["page"] + 1,
                }
            yield results
            json["search"]["page"] += 1

    def get_db(self):
        return self.search_by_keyword("", False)
