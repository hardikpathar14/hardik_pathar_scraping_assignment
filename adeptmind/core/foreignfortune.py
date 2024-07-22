import json
import pyuser_agent
import requests
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

    def parse_url(self, url):
        url_response = urlopen(url)
        htmlparser = etree.HTMLParser()
        response = etree.parse(url_response, htmlparser)

        ### Product ID
        product_id = (response.xpath("//meta[@property='og:url']/@content"))[0].split("/")[-1]

        ### Title
        title = ((response.xpath("//meta[@property='og:title']/@content"))[0]).title()

        ### Image
        image = (response.xpath("//meta[@property='og:image:secure_url']/@content"))[0]

        ### Price
        price = (response.xpath("//meta[@property='og:price:amount']/@content"))[0]

        ### Description
        description = (response.xpath("//meta[@property='og:description']/@content"))[0]

        ### List of Sale prices
        sale_prices = []

        ### List of Prices
        prices = []

        ### List of Images
        list_of_product_image = response.xpath("//img[@class='product-single__thumbnail-image']/@src")
        images = ["https:" + i if "http" not in i else i for i in list_of_product_image ]

        ### URL
        url = (response.xpath("//meta[@property='og:url']/@content"))[0]

        ### Brand
        brand = json.loads(response.xpath("//script[@type='application/ld+json']/text()")[1])["brand"]["name"]

        ### Models
        temp_var = json.loads(response.xpath("//script[@type='application/ld+json']/text()")[1])["offers"]
        list_model = list()
        for each in temp_var:
            ## Availability
            availability = each.get("availability").split("/")[-1]
            ## ID
            _id = each.get("url").split("?")[1].split("=")[1]
            ## Image
            model_image = each.get("itemOffered").get("image")
            ## Price
            price = each.get("price")
            ## Size
            size = each.get("itemOffered").get("name").split("/")[0]
            ## Colour
            colour = ""
            if len(each.get("itemOffered").get("name").split("/")) > 1:
                colour = each.get("itemOffered").get("name").split("/")[1]
            list_model.append(
                {
                "id": _id,
                "image": model_image,
                "price": price,
                "colour": colour,
                "size": size
                })

        return {
                    'product_id': product_id,
                    'title': title,
                    'image': image,
                    'price': price,
                    'description': description,
                    'images': images,
                    'url': url,
                    'brand': brand,
                    'availability': availability,
                    'models': {"variants": list_model}
                }

    def governor(self, URL, HEADER):
        ### Getting the sitemap URL
        urls = self.scraping(URL, HEADER)
        sites_to_scrap = [i for i in urls if "products" in i][0]

        ### Getting Product URL
        temp_list = [self.scraping(sites_to_scrap, HEADER)]
        list_of_product_url = list(itertools.chain.from_iterable(temp_list))

        ### Scraping each Product URL
        list_of_result = list()
        for each_url in list_of_product_url:
            if ("/products/" in each_url or "/product/" in each_url):
                ### Scraping the web page
                temp_result = self.parse_url(each_url)
                ### Validating the result
                result = self.validation_obj.main(temp_result)
                if result:
                    list_of_result.append(result)
        ### Convert the output list into DataFrame
        df = pd.DataFrame(list_of_result)
        ### Storing DataFrame into CSV file
        df.to_csv("output/foreignfortune.csv")

if __name__ == "__main__":
    URL = "https://foreignfortune.com/sitemap.xml"
    HEADER = {"User-Agent" : pyuser_agent.UA().random}
    obj = WebScraping()
    obj.governor(URL, HEADER)
