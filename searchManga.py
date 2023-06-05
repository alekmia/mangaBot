import requests
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def search(name):
    # name = "Blue Lock"
    PATH = "C:\Program Files (x86)\geckodriver.exe"

    searchUrl = "https://mangareader.to/"

    s = Service(PATH)
    driver = webdriver.Firefox(service=s)
    driver.get(searchUrl)

    sleep(1)
    searchBar = driver.find_element(By.XPATH, '/html/body/div[3]/div[4]/div[1]/div/div/div[1]/div[1]/form/input')
    searchBar.send_keys(name)
    sleep(0.5)
    searchBar.send_keys(Keys.RETURN)
    sleep(1)

    # searchList = driver.find_element(By.XPATH, '//*[@id="main-content"]/section/div[2]/div[1]')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    searchElements = soup.find_all(class_="manga-name")
    new_elements = []
    for element in searchElements:
        d = {}
        d['href'] = element.find('a', href=True)['href']
        d['title'] = element.text
        new_elements.append(d)
    driver.quit()

    return new_elements

