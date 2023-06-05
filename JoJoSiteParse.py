import requests
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

database = {"jojo":
                {"url": "https://mangareader.to/jojos-bizarre-adventure-part-9-the-jojolands-64643?ref=search",
                 "Name": "JoJo's Bizarre Adventure: JoJoLands"}}

jojo9Url = "https://mangareader.to/jojos-bizarre-adventure-part-9-the-jojolands-64643?ref=search"

def parseSite(url):
    caps = DesiredCapabilities().FIREFOX
    caps["pageLoadStrategy"] = "eager"
    firefoxProfile = webdriver.FirefoxProfile()
    firefoxProfile.set_preference('permissions.default.stylesheet', 2)
    firefoxProfile.set_preference('permissions.default.image', 2)
    firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    firefoxProfile.set_preference("http.response.timeout", 10)
    firefoxProfile.set_preference("dom.max_script_run_time", 10)
    PATH = "C:\Program Files (x86)\geckodriver.exe"
    s = Service(PATH)
    driver = webdriver.Firefox(desired_capabilities=caps, firefox_profile=firefoxProfile, service=s)
    driver.get(url)
    chapter_list = driver.find_element(By.ID, "en-chapters").text.splitlines()
    amount = len(chapter_list)
    print(amount, "\nlatest chapter is ", chapter_list[0])
    driver.quit()

    return amount, chapter_list[0]

def parseJojo():
    PATH = "C:\Program Files (x86)\geckodriver.exe"
    s = Service(PATH)
    driver = webdriver.Firefox(service=s)
    driver.get(jojo9Url)
    chapter_list = driver.find_element(By.ID, "en-chapters").text.splitlines()
    amount = len(chapter_list)
    print(amount, "\nlatest chapter is ", chapter_list[0])
    driver.quit()

    return amount, chapter_list[0]
