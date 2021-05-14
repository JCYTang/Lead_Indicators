from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraping_indicators.spiders.apra_spider import ApraSpider
from scraping_indicators.spiders.ica_spider import IcaSpider
from scraping_indicators.spiders.moneyfacts_spider import MoneyfactsSpider
from scraping_indicators.spiders.nationwide_spider import NationwideSpider
from scraping_indicators.spiders.marsh_spider import MarshSpider


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    Crawler = process.create_crawler(MarshSpider)
    process.crawl(Crawler)
    process.start() # the script will block here until the crawling is finished