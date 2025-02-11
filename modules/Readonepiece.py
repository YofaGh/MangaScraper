from bs4 import BeautifulSoup
from utils.models import Manga


class Readonepiece(Manga):
    domain = "readonepiece.com"
    logo = "https://ww9.readonepiece.com/apple-touch-icon.png"

    def get_info(manga):
        response, _ = Readonepiece.send_request(
            f"https://ww9.readonepiece.com/manga/{manga}/"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        cover = soup.find("div", {"class": "py-4 px-6 mb-3"}).find("img")["src"]
        title = soup.find(
            "h1", {"class": "my-3 font-bold text-2xl md:text-3xl"}
        ).get_text(strip=True)
        summary = (
            soup.find("div", {"class": "py-4 px-6 mb-3"})
            .find("div", {"class": "text-text-muted"})
            .get_text(strip=True)
        )
        return {
            "Cover": cover,
            "Title": title,
            "Summary": summary,
        }

    def get_chapters(manga):
        response, _ = Readonepiece.send_request(
            f"https://ww9.readonepiece.com/manga/{manga}/"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        divs = soup.find_all(
            "div", {"class": "bg-bg-secondary p-3 rounded mb-3 shadow"}
        )
        chapters = [div.find("a")["href"].split("/")[-2] for div in divs[::-1]]
        chapters_urls = [chapter.replace(f"{manga}-", "") for chapter in chapters]
        chapters = [
            {"url": chapter_url, "name": Readonepiece.rename_chapter(chapter_url)}
            for chapter_url in chapters_urls
        ]
        return chapters

    def get_images(manga, chapter):
        chapter_url = chapter["url"]
        if f"{manga}-" in chapter_url:
            chapter_url = chapter_url.replace(f"{manga}-", "")
        response, _ = Readonepiece.send_request(
            f"https://ww9.readonepiece.com/chapter/{manga}-{chapter_url}"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        images = soup.find_all("img", {"class", "mb-3 mx-auto js-page"})
        images = [image["src"] for image in images]
        return images, False

    def search_by_keyword(keyword, absolute):
        response, _ = Readonepiece.send_request(
            "https://ww11.readonepiece.com/sitemap.xml"
        )
        soup = BeautifulSoup(response.text, "xml")
        results = {}
        urls = soup.find_all("url")
        for url in urls:
            priority = url.find("priority").get_text()
            if priority != "0.8":
                break
            manga_url = url.find("loc").get_text().split("/")[-2]
            name = manga_url.replace("-", " ")
            if absolute and keyword.lower() not in name.lower():
                continue
            results[name] = {
                "domain": Readonepiece.domain,
                "url": manga_url,
                "page": 1,
            }
        yield results
        yield {}

    def get_db():
        return Readonepiece.search_by_keyword("", False)
