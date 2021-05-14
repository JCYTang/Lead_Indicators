import scrapy
from scraping_indicators.items import DownloadFileItem
from datetime import datetime, timedelta


class NationwideSpider(scrapy.Spider):
    name = 'nationwide'
    start_urls = [
        'https://www.nationwide.co.uk/-/media/MainSite/documents/about/house-price-index/downloads/quarterly.xls'
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'scraping_indicators.pipelines.NationwideFilesPipeline': 1,
        },
        'DOWNLOADER_MIDDLEWARES': {},
    }

    def parse(self, response):
        if response.status == 200:
            yield DownloadFileItem(file_urls=[response.url])