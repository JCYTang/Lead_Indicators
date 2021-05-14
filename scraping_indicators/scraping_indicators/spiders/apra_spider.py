import scrapy
from scraping_indicators.items import DownloadFileItem


class ApraSpider(scrapy.Spider):
    name = 'apra'
    start_urls = [
        'https://www.apra.gov.au/quarterly-general-insurance-statistics'
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'scraping_indicators.pipelines.ApraIndicatorsPipeline': 300,
            'scraping_indicators.pipelines.ApraFilesPipeline': 1,
        },
        'DOWNLOADER_MIDDLEWARES': {},
    }

    def parse(self, response):
        file_urls = response.xpath('//a[contains(@href, "xlsx")]/@href').extract()
        matches = ['database', 'performance']
        for url in file_urls:
            if all(word in url for word in matches):
                yield DownloadFileItem(file_urls=[url])