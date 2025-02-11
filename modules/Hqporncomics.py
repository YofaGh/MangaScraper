from utils.models import Doujin


class Hqporncomics(Doujin):
    domain = "hqporncomics.com"
    logo = "https://hqporncomics.com/images/favicon.ico"
    is_coded = False

    def get_info(self, code):
        from contextlib import suppress

        response, _ = self.send_request(f"https://hqporncomics.com/comics/{code}/")
        soup = self.get_html_parser(response.text)
        cover, title, summary, pages = 4 * [""]
        extras = {}
        images = soup.find("div", {"id": "block-image-slide"}).find_all("img")
        images = [image["data-src"] for image in images[::2]]
        with suppress(Exception):
            cover = images[0]
        with suppress(Exception):
            title = (
                soup.find("h1", {"class": "block-name-comix"})
                .get_text(strip=True)
                .strip("Porn comic ")
            )
        with suppress(Exception):
            pages = len(images)
        with suppress(Exception):
            summary = soup.find("div", {"class": "mini-description"}).get_text(
                strip=True
            )
        extras_raw = soup.find_all("div", {"class": "category-spisok"})
        for extra_raw in extras_raw:
            with suppress(Exception):
                extras[extra_raw.find("li").get_text(strip=True).rstrip(":")] = [
                    link.get_text(strip=True) for link in extra_raw.find_all("a")
                ]
        return {
            "Cover": cover,
            "Title": title,
            "Pages": pages,
            "Summary": summary,
            "Extras": extras,
        }

    def get_title(self, code):
        response, _ = self.send_request(f"https://hqporncomics.com/comics/{code}/")
        soup = self.get_html_parser(response.text)
        title = (
            soup.find("h1", {"class": "block-name-comix"})
            .get_text(strip=True)
            .strip("Porn comic ")
        )
        return title

    def get_images(self, code):
        response, _ = self.send_request(f"https://hqporncomics.com/comics/{code}/")
        soup = self.get_html_parser(response.text)
        images = soup.find("div", {"id": "block-image-slide"}).find_all("img")
        images = [image["data-src"] for image in images[::2]]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1]}" for i in range(len(images))
        ]
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        page = 1
        prev_page = []
        session = None
        while True:
            response, session = self.send_request(
                f"https://hqporncomics.com/search/?q={keyword}&page={page}",
                session=session,
            )
            soup = self.get_html_parser(response.text)
            doujins = soup.find_all("li", {"id": "li-comix-set"})
            if not doujins or prev_page == doujins:
                yield {}
            results = {}
            for doujin in doujins:
                title = doujin.find("h2").get_text(strip=True).strip("Porn comic ")
                if absolute and keyword.lower() not in title.lower():
                    continue
                likes, views, date, tags = "", "", "", []
                likes = doujin.find_all("li")[0].find("i").get_text(strip=True)
                views = doujin.find_all("li")[1].find("i").get_text(strip=True)
                date = doujin.find_all("li")[2].find("i").get_text(strip=True)
                if doujin.find("ul", {"class": "tags_ul"}):
                    tags = [
                        tag.get_text(strip=True).rstrip(" /")
                        for tag in doujin.find("ul", {"class": "tags_ul"}).find_all(
                            "a"
                        )[1:]
                    ]
                results[title] = {
                    "domain": self.domain,
                    "code": doujin.find("a")["href"].split("/")[-2],
                    "thumbnail": doujin.find("img")["data-src"],
                    "page": page,
                    "likes": likes,
                    "views": views,
                    "date": date,
                    "tags": tags,
                }
            prev_page = doujins
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)
