import scrapy
from scraping_indicators.items import DownloadFileItem
from datetime import datetime, timedelta
import math

dt_today = datetime.today()
current_qtr = math.ceil(dt_today.month / 3)
last_qtr_date = datetime(dt_today.year, 3 * current_qtr - 2, 1) - timedelta(days=1)
yr = str(last_qtr_date.year)
mth = str(last_qtr_date.month)

class IcaSpider(scrapy.Spider):
    name = 'ica'
    start_urls = [
        'https://www.insurancecouncil.com.au/assets/statistic/' + yr + ' Domestic Insurance Trends/' + yr + '-' + mth +
        ' ISA Home-building-contents - MV Data for ICA Data Project.xlsx'
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            # 'scraping_indicators.pipelines.IcaIndicatorsPipeline': 300,
            'scraping_indicators.pipelines.IcaFilesPipeline': 1,
        },
        'DOWNLOADER_MIDDLEWARES': {},
    }

    def parse(self, response):
        if response.status == 200:
            yield DownloadFileItem(file_urls=[response.url])