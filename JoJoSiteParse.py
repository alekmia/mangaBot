from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


def parseSite(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    chapter_list = driver.find_element(By.ID, "en-chapters").text.splitlines()
    amount = len(chapter_list)
    print(amount, "\nlatest chapter is ", chapter_list[0])
    driver.quit()

    return amount, chapter_list[0]
