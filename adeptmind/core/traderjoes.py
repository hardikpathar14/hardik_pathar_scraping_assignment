from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import requests
import json
import pyuser_agent
from bs4 import BeautifulSoup
from datetime import datetime
import itertools
from urllib.request import urlopen
from lxml import etree
from helper.validation import Validation
import pandas as pd


class WebScraping():
    def __init__(self):
        self.validation_obj = Validation()

    def scraping(self, URL, HEADER):
        page = requests.get(URL, headers=HEADER)
        soup = BeautifulSoup(page.content, "html.parser")
        job_elements = soup.find_all("loc")
        urls = [i.text for i in job_elements]
        return urls

    def get_price_and_description_from_url(self,url):
        # Set up Selenium options
        options = Options()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        # Initialize the WebDriver
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        path_ = driver.service.path
        print(path_)
        
        try:
            # Open the URL
            driver.get(url)
            
            # Wait for the price element to be present
            wait = WebDriverWait(driver, 10)
            price_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ProductPrice_productPrice__price__3-50j')))
            
            # Get the price text content
            price = price_element.text
            
            # Wait for the description div to be present
            description_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Expand_expand__container__3COzO')))
            
            # Set the style using JavaScript
            driver.execute_script("""
                var elements = document.getElementsByClassName('Expand_expand__container__3COzO');
                for (var i = 0; i < elements.length; i++) {
                    elements[i].style.maxHeight = 'unset';
                    elements[i].style.webkitLineClamp = '9999999';
                }
            """)
            
            # Get all paragraph texts within the description div
            paragraphs = description_element.find_elements(By.TAG_NAME, 'p')
            description = '\n'.join([paragraph.text for paragraph in paragraphs])
            
            return price, description
        finally:
            # Close the browser
            driver.quit()
    
    def parse_url(self, url):
        url_response = urlopen(url)
        htmlparser = etree.HTMLParser()
        response = etree.parse(url_response, htmlparser)

        ### Product ID
        product_id = (response.xpath("//meta[@property='og:url']/@content"))[0].split("/")[-1]

        ### Title
        title = ((response.xpath("//meta[@property='og:title']/@content"))[0]).title()

        ### Image
        image = (response.xpath("//meta[@property='og:image']/@content"))[0]
        # import pdb; pdb.set_trace()
        ### Price & Description
        price, description = self.get_price_and_description_from_url(url)

        ### URL
        url = (response.xpath("//meta[@property='og:url']/@content"))[0]

        ### List of Sale prices
        sale_prices = []

        ### List of Prices
        prices = []

        ### List of Images
        # list_of_product_image = response.xpath("//img[@class='product-single__thumbnail-image']/@src")
        # images = ["https:" + i if "http" not in i else i for i in list_of_product_image ]

        ### Brand
        # brand = json.loads(response.xpath("//script[@type='application/ld+json']/text()")[1])["brand"]["name"]
        return {
                    'product_id': product_id,
                    'title': title,
                    'image': image,
                    'price': price,
                    'description': description,
                    'images': [],
                    'url': url,
                    'brand': "",
                    'availability': "",
                    'models': {"variants": []}
                }


    def governor(self, URL, HEADER):
        ### Getting Product URL
        urls = self.scraping(URL, HEADER)
        list_of_product_url = [i for i in urls if "/products/pdp/" in i]

        ### Scraping each Product URL
        list_of_result = list()
        for index, each_url in enumerate(list_of_product_url):
            print("{}: {}".format(index, each_url))
            ### Scraping the web page
            temp_result = self.parse_url(each_url)
            print(temp_result)
            ### Validating the result
            # result = self.validation_obj.main(temp_result)
            # if temp_result:
            list_of_result.append(temp_result)

        ### Convert the output list into DataFrame
        df = pd.DataFrame(list_of_result)
        ### Storing DataFrame into CSV file
        df.to_csv("output/traderjoes.csv")


if __name__ == "__main__":
    URL = "https://traderjoes.com/sitemap.xml"
    HEADER = {"User-Agent" : pyuser_agent.UA().random}
    obj = WebScraping()
    obj.governor(URL, HEADER)
