from utils.models import Doujin
from user_agents import MOZILLA


class _999hentai(Doujin):
    domain = "999hentai.net"
    logo = "https://999hentai.net/icons/icon-32x32.ico"
    headers = {"User-Agent": MOZILLA}
    is_coded = False

    def get_info(self, code):
        from contextlib import suppress

        response, _ = self.send_request(
            f"https://999hentai.net/hchapter/{code}", headers=self.headers
        )
        soup = self.get_html_parser(response.text)
        cover, title, pages = "", "", ""
        extras = {}
        with suppress(Exception):
            host = soup.find(
                lambda tag: tag.name == "meta" and tag.get("property") == "og:image"
            )["content"].rsplit("/", 1)[0]
            cover = (
                soup.find(lambda tag: tag.name == "script" and "__NUXT__" in tag.text)
                .get_text(strip=True)
                .split("pics:[", 1)[1]
            )
            cover = cover.split('url:"', 1)[1].split('",', 1)[0]
            cover = f"{host}/{cover}"
        with suppress(Exception):
            title = soup.find("h1").get_text(strip=True)
        for div in soup.find("div", {"class": "col-md-8 col-sm-12"}).find_all(
            "div", recursive=False
        ):
            if "Page" in div.text:
                with suppress(Exception):
                    pages = div.get_text(strip=True).replace("Page:", "")
            elif "Tags" in div.text:
                with suppress(Exception):
                    extras["Tags"] = [
                        a.contents[0].strip().capitalize() for a in div.find_all("a")
                    ]
            else:
                tag_name = div.find("span").get_text(strip=True)
                with suppress(Exception):
                    extras[tag_name.rstrip(":")] = div.get_text(strip=True).replace(
                        tag_name, ""
                    )
        return {"Cover": cover, "Title": title, "Pages": pages, "Extras": extras}

    def get_title(self, code):
        response, _ = self.send_request(
            f"https://999hentai.net/hchapter/{code}", headers=self.headers
        )
        soup = self.get_html_parser(response.text)
        title = soup.find("h1").get_text(strip=True)
        return title

    def get_images(self, code):
        response, _ = self.send_request(
            f"https://999hentai.net/hchapter/{code}", headers=self.headers
        )
        soup = self.get_html_parser(response.text)
        images = (
            soup.find(lambda tag: tag.name == "script" and "__NUXT__" in tag.text)
            .get_text(strip=True)
            .split("pics:[", 1)[1]
            .split("],picsS")[0]
        )
        images = [
            image.split('url:"', 1)[1].split('",', 1)[0]
            for image in images.split("},{")
        ]
        host = soup.find(
            lambda tag: tag.name == "meta" and tag.get("property") == "og:image"
        )["content"].rsplit("/", 1)[0]
        images = [f"{host}/{image}" for image in images]
        return images, False
