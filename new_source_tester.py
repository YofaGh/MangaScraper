import requests, time, sys, os
from bs4 import BeautifulSoup
from assets import rename_chapter, create_path
from sources import Manhwa18, Manhuascan
from PIL import Image

'''headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
}'''

def get_chapters():
    response = requests.get('https://mangareader.cc/manga/secret-class')
    soup = BeautifulSoup(response.text, 'html.parser')
    chapters = soup.find('div', {'class':'cl'}).find_all('a')
    for chapter in chapters:
        print(chapter['href'], rename_chapter(chapter['href'].split('/')[-1]))

def get_images():
    response = requests.get('https://mangareader.cc/chapter/secret-class-chapter-137#1')
    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find('div', {'id':'readerarea'}).find('img')
    print(images)
    '''print(images)
    for image in images:
        print(image['data-src'].strip())

    with open('001.jpg', 'wb') as image:
        image.write(requests.get(images[0]['data-src'].strip()).content)'''

#get_chapters()
#get_images()