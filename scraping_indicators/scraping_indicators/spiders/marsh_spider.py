import scrapy
from scraping_indicators.items import DownloadFileItem
from datetime import datetime, timedelta
import math

dt_today = datetime.today()
current_qtr = math.ceil(dt_today.month / 3)
last_qtr_date = datetime(dt_today.year, 3 * current_qtr - 2, 1) - timedelta(days=1)
last_qtr = str(math.ceil(last_qtr_date.month / 3))
yr = str(last_qtr_date.year)


class MarshSpider(scrapy.Spider):
    name = 'marsh'
    start_urls = [
        'https://www.marsh.com/us/insights/research/global-insurance-market-index-q' + last_qtr + '-' + yr + '.html'
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'scraping_indicators.pipelines.MarshFilesPipeline': 1,
        },
        'DOWNLOADER_MIDDLEWARES': {},
    }

    def parse(self, response):
        if response.status == 200:
            file_url = response.xpath('//@data-csv-url').get()
            file_url = 'https://www.marsh.com' + file_url
            yield DownloadFileItem(file_urls=[file_url])