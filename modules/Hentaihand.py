from utils.models import Doujin


class Hentaihand(Doujin):
    domain = "hentaihand.com"
    logo = "https://hentaihand.com/images/icon.png"
    is_coded = False

    def get_info(self, code):
        response, _ = self.send_request(f"https://hentaihand.com/api/comics/{code}")
        response = response.json()
        extras = {
            "Description": response["description"],
            "Category": response.get("category", {}).get("name") or "",
            "Language": response.get("language", {}).get("name") or "",
            "Tag": [tag["name"] for tag in response["tags"]],
            "Parodies": [parody["name"] for parody in response["parodies"]],
            "Artists": [artist["name"] for artist in response["artists"]],
            "Authors": [author["name"] for author in response["authors"]],
            "Groups": [group["name"] for group in response["groups"]],
            "Characters": [character["name"] for character in response["characters"]],
            "Relationships": [
                relationship["name"] for relationship in response["relationships"]
            ],
        }
        return {
            "Cover": response["image_url"],
            "Title": response["title"],
            "Pages": response["pages"],
            "Alternative": response["alternative_title"],
            "Extras": extras,
            "Dates": {"Uploaded At": f"{response['uploaded_at']} 00:00:00"},
        }

    def get_title(self, code):
        response, _ = self.send_request(f"https://hentaihand.com/api/comics/{code}")
        return response.json()["title"]

    def get_images(self, code):
        response, _ = self.send_request(
            f"https://hentaihand.com/api/comics/{code}/images"
        )
        images = [image["source_url"] for image in response.json()["images"]]
        return images, False

    def search_by_keyword(self, keyword, absolute):
        params = {
            "page": 1,
            "q": keyword,
            "sort": "title",
        }
        session = None
        while True:
            response, session = self.send_request(
                "https://hentaihand.com/api/comics", session=session, params=params
            )
            response = response.json()
            if not response["data"]:
                yield {}
            results = {}
            for doujin in response["data"]:
                if absolute and keyword.lower() not in doujin["title"].lower():
                    continue
                results[doujin["title"]] = {
                    "domain": self.domain,
                    "code": doujin["slug"],
                    "thumbnail": doujin["image_url"],
                    "alternative": doujin["alternative_title"],
                    "category": doujin["category"]["name"]
                    if doujin["category"]
                    else "",
                    "language": doujin["language"]["name"]
                    if doujin["language"]
                    else "",
                    "tags": [tag["name"] for tag in doujin["tags"]],
                    "total_pages": doujin["pages"],
                    "uploaded_at": f"{doujin['uploaded_at']} 00:00:00",
                    "page": params["page"],
                }
            yield results
            params["page"] += 1

    def get_db(self):
        return self.search_by_keyword("", False)
