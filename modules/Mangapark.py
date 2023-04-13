import time
from bs4 import BeautifulSoup
from selenium import webdriver
from utils.Bases import Manga, Req
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class Mangapark(Manga, Req):
    def get_chapters(manga):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://mangapark.to/title/{manga}')
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        WebDriverWait(browser, 60).until(ec.presence_of_element_located((By.XPATH, '//div[@class="flex flex-col border-l rounded-l odd:border-primary even:border-secondary"]')))
        chapters = [link['href'] for link in soup.find_all('a', {'class': 'link-hover link-primary visited:text-accent'})]
        buttons = browser.find_elements(By.XPATH, "//button[@class='btn btn-xs  btn-primary mr-2 mt-2 btn-outline']")
        for button in buttons:
            button.click()
            WebDriverWait(browser, 60).until(ec.presence_of_element_located((By.XPATH, '//div[@class="flex flex-col border-l rounded-l odd:border-primary even:border-secondary"]')))
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            chapters += [link['href'] for link in soup.find_all('a', {'class': 'link-hover link-primary visited:text-accent'})]
        ctd = [chapters[0].split('/')[-1]]
        for i in range(1,len(chapters)):
            if chapters[i-1].split('-')[-1] != chapters[i].split('-')[-1]:
                ctd.insert(0, chapters[i].split('/')[-1])
        return ctd

    def get_images(manga, chapter):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        browser.get(f'https://mangapark.to/title/{manga}/{chapter}')
        load_all_images_button = browser.find_elements(By.XPATH, "//button[@class='btn btn-sm btn-info btn-outline btn-block normal-case opacity-80']")[1]
        load_all_images_button.click()
        time.sleep(10)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        images = soup.find_all('img', {'class': 'z-10 absolute top-0 right-0 bottom-0 left-0 w-full h-full'})
        images = [image['src'] for image in images]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search(title, absolute):
        from contextlib import suppress
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        service = Service(executable_path='geckodriver.exe', log_path='NUL')
        browser = webdriver.Firefox(options=options, service=service)
        page = 1
        prev_page = {}
        while True:
            browser.get(f'https://mangapark.to/v5x-search?word={title}&page={page}')
            WebDriverWait(browser, 60).until(ec.presence_of_element_located((By.XPATH, '//div[@class="flex group border-b border-b-base-200 pb-5"]')))
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            divs = soup.find_all('div', {'class': 'flex group border-b border-b-base-200 pb-5'})
            if prev_page == divs:
                yield {}
            results = {}
            for div in divs:
                ti = div.find('h3', {'class': 'font-bold space-x-1 text-lg line-clamp-2'}).find('a')
                if absolute and title.lower() not in ti.contents[0].lower():
                    continue
                latest_chapter, genres = '', ''
                with suppress(Exception):
                    genres = div.find('div', {'class': 'flex items-center flex-wrap text-xs opacity-70'}).find_all('a')
                    genres = ', '.join([genre.find('span').contents[0] for genre in genres])
                with suppress(Exception):
                    latest_chapter = div.find('div', {'class': 'flex justify-between text-sm flex-wrap'}).find('a')['href'].split('/')[-1]
                results[ti.contents[0]] = {
                    'domain': 'mangapark.to',
                    'url': ti['href'].split('/')[-1],
                    'genres': genres,
                    'latest_chapter': latest_chapter
                }
            yield results
            page += 1
            prev_page = divs

    def get_db():
        return Mangapark.search('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return 'Chapter 000'
        chapter = chapter.split('-')[-1]
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'