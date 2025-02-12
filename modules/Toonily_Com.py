from utils.models import Manga


class Toonily_Com(Manga):
    domain = "toonily.com"
    logo = "https://toonily.com/wp-content/uploads/2020/01/cropped-toonfavicon-1-192x192.png"
    download_images_headers = {"Referer": "https://toonily.com/"}
    search_headers = {"cookie": "toonily-mature=1"}

    def get_info(self, manga):
        from contextlib import suppress

        response, _ = self.send_request(f"https://toonily.com/webtoon/{manga}/")
        soup = self.get_html_parser(response.text)
        (
            cover,
            title,
            alternative,
            summary,
            rating,
            status,
            authors,
            artists,
            genres,
            tags,
        ) = 10 * [""]
        info_box = soup.find("div", {"class": "tab-summary"})
        with suppress(Exception):
            cover = info_box.find("img")["data-src"]
        with suppress(Exception):
            title = (
                info_box.find("div", {"class": "post-title"})
                .find("h1")
                .contents[0]
                .strip()
            )
        with suppress(Exception):
            summary = soup.find("div", {"class": "summary__content"}).get_text(
                strip=True
            )
        with suppress(Exception):
            rating = float(
                soup.find("span", {"id": "averagerate"}).get_text(strip=True)
            )
        with suppress(Exception):
            status = (
                info_box.find("div", {"class": "post-status"})
                .find_all("div", {"class": "summary-content"})[1]
                .get_text(strip=True)
            )
        with suppress(Exception):
            tags = [
                tag.get_text(strip=True).replace("#", "")
                for tag in soup.find("div", {"class": "wp-manga-tags-list"}).find_all(
                    "a"
                )
            ]
        for box in soup.find("div", {"class": "manga-info-row"}).find_all(
            "div", {"class": "post-content_item"}
        ):
            if "Alt Name" in box.get_text(strip=True):
                alternative = box.find("div", {"class": "summary-content"}).get_text(
                    strip=True
                )
            elif "Author" in box.get_text(strip=True):
                authors = [a.get_text(strip=True) for a in box.find_all("a")]
            elif "Artist" in box.get_text(strip=True):
                artists = [a.get_text(strip=True) for a in box.find_all("a")]
            elif "Genre" in box.get_text(strip=True):
                genres = [a.get_text(strip=True) for a in box.find_all("a")]
        return {
            "Cover": cover,
            "Title": title,
            "Alternative": alternative,
            "Summary": summary,
            "Rating": rating,
            "Status": status,
            "Extras": {
                "Authors": authors,
                "Artists": artists,
                "Genres": genres,
                "Tags": tags,
            },
        }

    def get_chapters(self, manga):
        response, _ = self.send_request(f"https://toonily.com/webtoon/{manga}/")
        soup = self.get_html_parser(response.text)
        divs = soup.find_all("li", {"class": "wp-manga-chapter"})
        chapters_urls = [div.find("a")["href"].split("/")[-2] for div in divs[::-1]]
        chapters = [
            {"url": chapter_url, "name": self.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(self, manga, chapter):
        response, _ = self.send_request(
            f"https://toonily.com/webtoon/{manga}/{chapter['url']}/"
        )
        soup = self.get_html_parser(response.text)
        images = soup.find("div", {"class": "reading-content"}).find_all("img")
        images = [image["data-src"].strip() for image in images]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1]}" for i in range(len(images))
        ]
        return images, save_names

    def search_by_keyword(self, keyword, absolute):
        from requests.exceptions import HTTPError

        template = (
            f"https://toonily.com/search/{keyword}/page/P_P_P_P/"
            if keyword
            else "https://toonily.com/search/page/P_P_P_P/"
        )
        page = 1
        session = None
        while True:
            try:
                response, session = self.send_request(
                    template.replace("P_P_P_P", str(page)),
                    session=session,
                    headers=self.search_headers,
                )
            except HTTPError:
                yield {}
            soup = self.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "col-6 col-sm-3 col-lg-2"})
            results = {}
            for manga in mangas:
                details = manga.find("div", {"class": "post-title font-title"})
                if (
                    absolute
                    and keyword.lower() not in details.get_text(strip=True).lower()
                ):
                    continue
                results[details.get_text(strip=True)] = {
                    "domain": self.domain,
                    "url": details.find("a")["href"].split("/")[-2],
                    "thumbnail": manga.find("img")["data-src"],
                    "page": page,
                }
            yield results
            page += 1

    def get_db(self):
        return self.search_by_keyword("", False)
