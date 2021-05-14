# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader


class DownloadFileItem(scrapy.Item):
    # define the fields for your item here like:
    file_urls = scrapy.Field()
    files = scrapy.Field()


class MoneyFactsItem(scrapy.Item):
    Date = scrapy.Field()
    Id = scrapy.Field()
    Term = scrapy.Field()
    Company = scrapy.Field()
    Rate = scrapy.Field()
    MaxLTV = scrapy.Field()
