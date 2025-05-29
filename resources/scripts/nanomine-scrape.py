import os
import logging
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
# import pandas as pd
import time

logging.basicConfig(filename="nanomine-scrape.log", level=logging.INFO)

# Setup selenium with headless chrome
def setup_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome("/Users/anmolsaini/chromedriver-mac-x64/chromedriver", options=options)
    return driver

def main():
    data_dir = "../datasets/nanomine2"
    driver = setup_selenium()
    # url = "https://materialsmine.org/explorer/xmls"
    # loops for every xml
    for i in range(6830, 7280):
    # for i in range(7008, 7280):
        try:
            print(i)
            # gets xml selection page
            url = f"https://materialsmine.org/explorer/xmls?page={i}&size=1"
            driver.get(url)
            # time.sleep(0.05) # delay needed to allow page to load
            # time.sleep(0.6) # delay needed to allow page to load
            time.sleep(2.5) # delay needed to allow page to load, artificially inflated

            # goes to data of current xml
            soup = BeautifulSoup(driver.page_source, "lxml")
            md_card_class = soup.find("div", class_="md-card")
            # print(md_card_class)
            md_card_link = md_card_class.find("a", href=True)
            # print(md_card_link["href"])
            driver.get(f"https://materialsmine.org{md_card_link['href']}")
            time.sleep(2.5)

            # makes a local file with the extracted name and data of current xml
            soup = BeautifulSoup(driver.page_source, "lxml")
            xml_title = soup.find("h2", class_="visualize_header-h1")
            # print(xml_title.text)
            title_text = xml_title.text.strip()
            if title_text == "This XML no longer exists or has been moved":
                logging.warning(f"DNE: {i}")
                continue
            else:
                logging.info(f"{i} - {title_text}")
            with open(os.path.join(data_dir, title_text), "w") as f:
                # xml_data = soup.find("code", class_="inlinecode")
                xml_data = soup.find("code", class_="language-xml") # changed in update
                # f.write(str(xml_data))
                # print(xml_data)
                f.write(xml_data.text)
                # print(xml_data.text)
        except AttributeError:
            logging.error(f"Error: {i} - {title_text}")
            continue

    # driver = webdriver.Chrome("/Users/anmolsaini/chromedriver_mac64/chromedriver")
    # driver = webdriver.Chrome("/Users/anmolsaini/chromedriver-mac-x64/chromedriver")
    # driver = webdriver.Chrome("/Users/anmolsaini/chrome-headless-shell-mac-x64/chrome-headless-shell")
    # driver.get(url)
    # print(driver.title)

    driver.quit()

if __name__ == "__main__":
    main()
