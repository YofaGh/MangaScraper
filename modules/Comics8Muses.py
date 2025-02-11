from utils.models import Manga


class Comics8Muses(Manga):
    domain = "comics.8muses.com"
    logo = "https://comics.8muses.com/favicon.ico"

    def get_info(self, manga):
        response, _ = self.send_request(
            f"https://comics.8muses.com/comics/album/{manga}/"
        )
        soup = self.get_html_parser(response.text)
        return {
            "Cover": f"https://comics.8muses.com{soup.find('div', {'class': 'gallery'}).find('img')['data-src']}",
            "Title": soup.find("div", {"class": "top-menu-breadcrumb"})
            .find_all("li")[-1]
            .find("a")
            .get_text(strip=True),
        }

    def get_chapters(self, manga):
        page = 1
        chapters_urls = []
        response, session = self.send_request(
            f"https://comics.8muses.com/comics/album/{manga}/{page}"
        )
        soup = self.get_html_parser(response.text)
        if not soup.find("div", {"class": "image-title"}):
            return [""]
        while True:
            links = soup.find_all("a", {"class": "c-tile t-hover"}, href=True)
            if not links:
                break
            chapters_urls += [link.get("href").split("/")[-1] for link in links]
            page += 1
            response, session = self.send_request(
                f"https://comics.8muses.com/comics/album/{manga}/{page}",
                session=session,
            )
            soup = self.get_html_parser(response.text)
        chapters = [
            {"url": chapter_url, "name": self.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(self, manga, chapter):
        response, _ = self.send_request(
            f"https://comics.8muses.com/comics/album/{manga}/{chapter['url']}"
        )
        soup = self.get_html_parser(response.text)
        links = soup.find_all("a", {"class": "c-tile t-hover"})
        images = [link.find("img").get("data-src") for link in links]
        images = [
            f"https://comics.8muses.com/image/fm/{image.split('/')[-1]}"
            for image in images
        ]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1]}" for i in range(len(images))
        ]
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        page = 1
        links = []
        session = None
        while True:
            response, session = self.send_request(
                f"https://comics.8muses.com/search?q={keyword}&page={page}",
                session=session,
            )
            soup = self.get_html_parser(response.text)
            comics = soup.find_all("a", {"class": "c-tile t-hover"}, href=True)
            results = {}
            if not comics:
                yield {}
            for comic in comics:
                if not comic.get("href"):
                    continue
                if (
                    absolute
                    and keyword.lower() not in comic.get_text(strip=True).lower()
                ):
                    continue
                url = comic.get("href").replace(
                    "https://comics.8muses.com/comics/album/", ""
                )
                sublink = False
                for link in links:
                    if link in url:
                        sublink = True
                        break
                if not sublink:
                    links.append(url)
                    results[comic.get_text(strip=True)] = {
                        "domain": self.domain,
                        "url": url,
                        "thumbnail": f"https://comics.8muses.com{comic.find('img')['data-src']}",
                        "page": page,
                    }
            yield results
            page += 1

    def get_db(self):
        from requests.exceptions import HTTPError

        page = 1
        session = None
        while True:
            try:
                response, session = self.send_request(
                    f"https://comics.8muses.com/sitemap/{page}.xml", session=session
                )
            except HTTPError:
                yield {}
            soup = self.get_xml_parser(response.text)
            results = {}
            urls = soup.find_all("loc")
            for url in urls:
                results[url.get_text().split("/")[-1].replace("-", " ")] = {
                    "domain": self.domain,
                    "url": url.get_text().replace(
                        "https://comics.8muses.com/comics/album/", ""
                    ),
                    "page": page,
                }
            yield results
            page += 1

    @staticmethod
    def rename_chapter(name):
        return name.replace("-", " ")
