import requests
import json
import os
from bs4 import BeautifulSoup
from contextlib import suppress
from utils.logger import log_over, log
from utils.assets import save_json_file


def yandex(url: str) -> list[dict[str, str]]:
    response = requests.get(f"https://yandex.com/images/search?rpt=imageview&url={url}")
    soup = BeautifulSoup(response.text, "html.parser")
    data_raw = soup.find("div", {"class": "cbir-section cbir-section_name_sites"}).find(
        "div", {"class": "Root"}
    )["data-state"]
    data = json.loads(data_raw)
    sites = data["sites"]
    return [
        {"url": site["url"], "image": site["originalImage"]["url"]} for site in sites
    ]


def tineye(url: str) -> list[dict[str, str]]:
    headers = {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryVxauFLsZbD7Cr1Fa"
    }
    data = f'------WebKitFormBoundaryVxauFLsZbD7Cr1Fa\nContent-Disposition: form-data; name="url"\n\n{url}\n------WebKitFormBoundaryVxauFLsZbD7Cr1Fa--'
    response = requests.post(
        "https://tineye.com/result_json/?sort=score&order=desc&page=1",
        data=data,
        headers=headers,
    ).json()
    total_pages = response["total_pages"]
    matches = response["matches"]
    for i in range(2, total_pages + 1):
        response = requests.post(
            f"https://tineye.com/result_json/?sort=score&order=desc&page={i}",
            data=data,
            headers=headers,
        ).json()
        matches.extend(response["matches"])
    results = []
    for match in matches:
        for domain in match["domains"]:
            for backlink in domain["backlinks"]:
                results.append({"url": backlink["backlink"], "image": backlink["url"]})
    return results


def iqdb(url: str) -> list[dict[str, str]]:
    response = requests.get(f"https://iqdb.org/?url={url}")
    soup = BeautifulSoup(response.text, "html.parser")
    divs = [
        div
        for div in soup.find("div", {"id": "pages"}).find_all("div")
        if "Your image" not in div.text
    ]
    results = []
    for div in divs:
        with suppress(Exception):
            td = div.find("td", {"class": "image"})
            td_url = td.find("a")["href"]
            if "https:" not in td_url:
                td_url = "https:" + td_url
            td_image = td.find("img")["src"]
            if "https:" not in td_image:
                td_image = "https://iqdb.org" + td_image
            results.append({"url": td_url, "image": td_image})
    return results


def saucenao(url: str) -> list[dict[str, str]]:
    response = requests.get(f"https://saucenao.com/search.php?db=999&url={url}")
    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find("div", {"id": "middle"}).find_all("div", {"class": "result"})
    results = []
    for div in divs:
        if "Low similarity results have been hidden" in div.text:
            break
        with suppress(Exception):
            results.append(
                {
                    "url": div.find("div", {"class": "resultimage"}).find("a")["href"],
                    "image": None,
                }
            )
    return results


def sauce_file(path_to_file: str) -> str:
    log_over("\ruploading image to imgops.com")
    with open(path_to_file, "rb") as file:
        bytes = file.read()
    response = requests.post(
        "https://imgops.com/store",
        files={"photo": (os.path.basename(path_to_file), bytes)},
    )
    soup = BeautifulSoup(response.text, "html.parser")
    link = soup.find("div", {"id": "content"}).find("a")["href"]
    log("\rimage was successfully uploaded to imgops.com", "green")
    log("here is the link to the image:", "green")
    log(f"    https:{link}", "yellow")
    return f"https:{link}"


def sauce_url(url: str) -> None:
    results = {}
    for site in sites:
        temp_results = []
        log_over(f"\r{site.__name__}: searching image")
        with suppress(Exception):
            temp_results = site(url)
        log(
            f"\r{site.__name__}: {len(temp_results)} results were found.",
            "green" if temp_results else "yellow",
        )
        if temp_results:
            results[site.__name__] = temp_results
    save_json_file("sauce_output.json", results)
    print_output(results)
    log(
        "This was a summary of the saucer.\nYou can see the full results in sauce_output.json",
        "green",
    )


def print_output(results: dict[str, list[dict[str, str]]]) -> None:
    log("Summary:")
    for site in results:
        log(f"{site}:")
        for result in results[site][:5]:
            log(f"    url: {result['url']}, image: {result['image']}")


sites = [yandex, tineye, iqdb, saucenao]
