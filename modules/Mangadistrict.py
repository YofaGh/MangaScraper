from utils.models import Manga


class Mangadistrict(Manga):
    domain = "mangadistrict.com"
    logo = "https://mangadistrict.com/wp-content/uploads/2021/02/cropped-Copie-de-Copie-de-MANGADISTRICT_5-192x192.png"

    def get_info(manga):
        from contextlib import suppress

        response, _ = Mangadistrict.send_request(
            f"https://mangadistrict.com/read-scan/{manga}"
        )
        soup = Mangadistrict.get_html_parser(response.text)
        cover, title, alternative, summary, rating, status = 6 * [""]
        extras = {}
        info_box = soup.find("div", {"class": "tab-summary"})
        with suppress(Exception):
            cover = info_box.find("img")["src"]
        with suppress(Exception):
            title = (
                soup.find("div", {"class": "post-title"})
                .find("h1")
                .get_text(strip=True)
            )
        with suppress(Exception):
            summary = soup.find("div", {"class": "summary__content"}).get_text(
                strip=True
            )
        with suppress(Exception):
            rating = float(
                info_box.find("div", {"class": "post-total-rating"})
                .find("span")
                .get_text(strip=True)
            )
        with suppress(Exception):
            extras["Release"] = (
                info_box.find("div", {"class": "post-status"})
                .find_all("div", {"class": "summary-content"})[0]
                .get_text(strip=True)
            )
        with suppress(Exception):
            status = (
                info_box.find("div", {"class": "post-status"})
                .find_all("div", {"class": "summary-content"})[1]
                .get_text(strip=True)
            )
        for box in soup.find("div", {"class": "post-content"}).find_all(
            "div", {"class": "post-content_item"}
        ):
            if "Rating" in box.get_text(strip=True):
                continue
            elif "Alternative" in box.get_text(strip=True):
                with suppress(Exception):
                    alternative = box.find(
                        "div", {"class": "summary-content"}
                    ).get_text(strip=True)
            else:
                heading = (
                    box.find("div", {"class": "summary-heading"})
                    .get_text(strip=True)
                    .replace("(s)", "")
                )
                info = box.find("div", {"class": "summary-content"})
                if info.find("a"):
                    extras[heading] = [
                        a.get_text(strip=True) for a in info.find_all("a")
                    ]
                else:
                    extras[heading] = box.find(
                        "div", {"class": "summary-content"}
                    ).get_text(strip=True)
        return {
            "Cover": cover,
            "Title": title,
            "Alternative": alternative,
            "Summary": summary,
            "Rating": rating,
            "Status": status,
            "Extras": extras,
        }

    def get_chapters(manga):
        response, _ = Mangadistrict.send_request(
            f"https://mangadistrict.com/read-scan/{manga}/ajax/chapters/", method="POST"
        )
        soup = Mangadistrict.get_html_parser(response.text)
        divs = soup.find_all("li", {"class": "wp-manga-chapter"})
        chapters_urls = [div.find("a")["href"].split("/")[-2] for div in divs[::-1]]
        chapters = [
            {"url": chapter_url, "name": Mangadistrict.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(manga, chapter):
        response, _ = Mangadistrict.send_request(
            f"https://mangadistrict.com/read-scan/{manga}/{chapter['url']}/"
        )
        soup = Mangadistrict.get_html_parser(response.text)
        images = soup.find("div", {"class": "reading-content"}).find_all("img")
        images = [image["src"].strip() for image in images]
        save_names = [
            f"{i + 1:03d}.{images[i].split('.')[-1]}" for i in range(len(images))
        ]
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        from requests.exceptions import HTTPError

        page = 1
        template = (
            f"https://mangadistrict.com/page/P_P_P_P/?s={keyword}&post_type=wp-manga"
        )
        if not keyword:
            template = "https://mangadistrict.com/page/P_P_P_P/?s&post_type=wp-manga&m_orderby=alphabet"
        session = None
        while True:
            try:
                response, session = Mangadistrict.send_request(
                    template.replace("P_P_P_P", str(page)), session=session
                )
            except HTTPError:
                yield {}
            soup = Mangadistrict.get_html_parser(response.text)
            mangas = soup.find_all("div", {"class": "row c-tabs-item__content"})
            results = {}
            for manga in mangas:
                tilink = manga.find("div", {"class", "post-title"})
                if (
                    absolute
                    and keyword.lower() not in tilink.get_text(strip=True).lower()
                ):
                    continue
                latest_chapter, authors, artists, genres, status, release_date = (
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                )
                contents = manga.find_all("div", {"class": "post-content_item"})
                for content in contents:
                    with suppress(Exception):
                        if "Authors" in content.text:
                            authors = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Artists" in content.text:
                            artists = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Genres" in content.text:
                            genres = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Status" in content.text:
                            status = content.find(
                                "div", {"class": "summary-content"}
                            ).get_text(strip=True)
                        if "Release" in content.text:
                            release_date = content.find("a").get_text(strip=True)
                with suppress(Exception):
                    latest_chapter = (
                        manga.find("span", {"class": "font-meta chapter"})
                        .find("a")["href"]
                        .split("/")[-2]
                    )
                results[tilink.get_text(strip=True)] = {
                    "domain": Mangadistrict.domain,
                    "url": tilink.find("a")["href"].split("/")[-2],
                    "latest_chapter": latest_chapter,
                    "thumbnail": manga.find("img")["src"],
                    "genres": genres,
                    "authors": authors,
                    "artists": artists,
                    "status": status,
                    "release_date": release_date,
                    "page": page,
                }
            yield results
            page += 1

    def get_db():
        return Mangadistrict.search_by_keyword("", False)
