# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import yaml
import json
from datetime import datetime
import os
from celery import Celery
from helpers.gen_helpers import GenHelperMain

class WebCrawlingPipeline:
    def __init__(self):
        pass

    def open_spider(self, spider):
        filename = "output_folder/{}_{}.json".format(spider.name, str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")))
        filepath = os.path.abspath(filename)
        self.file = open(filepath, 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()