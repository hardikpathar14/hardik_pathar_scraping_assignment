import scrapy
import pyuser_agent
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import itertools
import json
from helper.validation import Validation

class ForeignfortuneSpider(scrapy.Spider):
    name = "foreignfortune"
    allowed_domains = ["foreignfortune.com"]
    start_urls = ["https://foreignfortune.com"]

    def __init__(self):
        self.URL = "https://foreignfortune.com/sitemap.xml"
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
        sites_to_scrap = [i for i in urls if "products" in i][0]

        temp_list = [self.scraping(sites_to_scrap, HEADER)]
        list_of_product_url = list(itertools.chain.from_iterable(temp_list))

        final_list_of_prod_url = list()
        for each_url in list_of_product_url:
            if ("/products/" in each_url or "/product/" in each_url):
                final_list_of_prod_url.append(each_url)

        return final_list_of_prod_url

    def parse(self, response):
        # import pdb; pdb.set_trace()
        ### Product ID
        product_id = (response.xpath("//meta[@property='og:url']/@content").extract())[0].split("/")[-1]

        ### Title
        title = ((response.xpath("//meta[@property='og:title']/@content").extract())[0]).title()

        ### Image
        image = (response.xpath("//meta[@property='og:image:secure_url']/@content").extract())[0]

        ### Price
        price = (response.xpath("//meta[@property='og:price:amount']/@content").extract())[0]

        ### Description
        description = (response.xpath("//meta[@property='og:description']/@content").extract())[0]

        ### List of Sale prices
        sale_prices = []

        ### List of Prices
        prices = []

        ### List of Images
        list_of_product_image = response.xpath("//img[@class='product-single__thumbnail-image']/@src").extract()
        images = ["https:" + i if "http" not in i else i for i in list_of_product_image ]

        ### URL
        url = (response.xpath("//meta[@property='og:url']/@content").extract())[0]

        ### Brand
        brand = json.loads(response.xpath("//script[@type='application/ld+json']/text()").extract()[1])["brand"]["name"]

        ### Models
        temp_var = json.loads(response.xpath("//script[@type='application/ld+json']/text()").extract()[1])["offers"]
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

        temp_result = {
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
        validation_obj = Validation()
        result = validation_obj.main(temp_result)
        # import pdb; pdb.set_trace()
        if result:
            yield result
