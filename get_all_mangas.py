import requests, time, json
from bs4 import BeautifulSoup

def get_all_mangas():
    mangas = {}
    main_url = 'https://manhuascan.us/manga-list?page='
    i = 1
    while True:
        print(f'Getting mangas of page: {i}')
        res = requests.get(f'{main_url}{i}')
        soup = BeautifulSoup(res.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'bigor'})
        if len(divs) == 0:
            break
        for div in divs:
            manga = div.find('a')
            mangas[manga['title']] = {
                "include": False,
                "url": manga['href'].split('/')[-1],
                "last_downloaded_chapter": None,
                "chapters": []
            }
        i += 1
        time.sleep(2)
    return mangas

mangas = get_all_mangas()
with open('all_mangas.json', 'w') as all_mangas:
    all_mangas.write(json.dumps(mangas, indent=4))