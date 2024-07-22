import scrapy
import pyuser_agent
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import itertools
import json


class TraderjoesSpider(scrapy.Spider):
    name = "traderjoes"
    allowed_domains = ["traderjoes.com"]
    start_urls = ["https://traderjoes.com"]

    def __init__(self):
        self.URL = "https://traderjoes.com/sitemap.xml"
        self.HEADER = {"User-Agent" : pyuser_agent.UA().random}
        self.start_urls = self.governor(self.URL, self.HEADER)

    def scraping(self, URL, HEADER):
        page = requests.get(URL, headers=HEADER)
        soup = BeautifulSoup(page.content, "html.parser")
        job_elements = soup.find_all("loc")
        urls = [i.text for i in job_elements]
        return urls

    def governor(self, URL, HEADER):
        urls = self.scraping(URL, HEADER)
        sites_to_scrap = [i for i in urls if "/products/pdp/" in i]
        return sites_to_scrap

    def parse(self, response):
        import pdb; pdb.set_trace()
        ### Product ID
        product_id = (response.xpath("//meta[@property='og:url']/@content").extract())[0].split("/")[-1]

        ### Title
        title = ((response.xpath("//meta[@property='og:title']/@content").extract())[0]).title()

        ### Image
        image = (response.xpath("//meta[@property='og:image']/@content").extract())[0]

        ### Price
        price = (response.xpath("//span[@class='ProductPrice_productPrice__price__3-50j']/text()").extract())[0]

        ### Description
        description = (response.xpath("//meta[@property='og:description']/@content").extract())[0]

        ### List of Sale prices
        sale_prices = []

        ### List of Prices
        prices = []

        ### List of Images
        images = []

        ### URL
        url = (response.xpath("//meta[@property='og:url']/@content").extract())[0]

        ### Brand
        brand = ""

        ### Models
        temp_var = json.loads(response.xpath("//script[@type='application/ld+json']/text()").extract()[1])["offers"]
        list_model = list()
        for each in temp_var:
            ## ID
            _id = each.get("url").split("?")[1].split("=")[1]
            ## Image
            if each.get("itemOffered").get("image"):
                model_image = each.get("itemOffered").get("image")
            else:
                model_image = image
            ## Price
            price = each.get("price")
            ## Size
            size = each.get("itemOffered").get("name").split("/")[-1]
            ## Colour
            colour = ""
            if len(each.get("itemOffered").get("name").split("/")) > 1:
                colour = each.get("itemOffered").get("name").split("/")[0]
            list_model.append(
                {
                "id": _id,
                "image": model_image,
                "price": price,
                "colour": colour,
                "size": size
                })
        models = {"variants": list_model}

        yield {
                'product_id': product_id,
                'title': title,
                'image': image,
                'price': price,
                'description': description,
                'images': images,
                'url': url,
                'brand': brand,
                'models': models
            }
        

