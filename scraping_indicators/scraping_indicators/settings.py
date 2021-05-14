# Scrapy settings for scraping_indicators project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from shutil import which
from datetime import datetime, timedelta

end_of_prev_mth = datetime.today().replace(day=1) - timedelta(days=1)
end_of_prev_mth_file_string = end_of_prev_mth.strftime('%Y-%m-%d')
end_of_prev_mth = end_of_prev_mth.strftime('%d-%m-%Y')

BOT_NAME = 'scraping_indicators'

SPIDER_MODULES = ['scraping_indicators.spiders']
NEWSPIDER_MODULE = 'scraping_indicators.spiders'

# selenium settings
SELENIUM_DRIVER_NAME = 'firefox'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
SELENIUM_DRIVER_ARGUMENTS=['-headless']


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scraping_indicators (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'scraping_indicators.middlewares.ScrapingIndicatorsSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    'scraping_indicators.middlewares.ScrapingIndicatorsDownloaderMiddleware': 543,
    'scrapy_selenium.SeleniumMiddleware': 800,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'scraping_indicators.pipelines.ApraIndicatorsPipeline': 300,
    'scraping_indicators.pipelines.ApraFilesPipeline': 1,
    # 'scraping_indicators.pipelines.IcaIndicatorsPipeline': 300,
    'scraping_indicators.pipelines.IcaFilesPipeline': 1,
    'scraping_indicators.pipelines.MoneyfactsPipeline': 300,
    'scraping_indicators.pipelines.NationwideFilesPipeline': 1,
}
PROJECT_ROOT = os.path.abspath('.')
FILES_STORE = os.path.join(os.path.dirname(PROJECT_ROOT), 'dash-indicators\data')
# FILES_STORE = 'C:\\Users\\jeremy.tang\\OneDrive - IML AU\\Investment Team\\Lead Indicators\\dash-indicators\\data'

# 1 day of delay for files expiration
APRAFILESPIPELINE_FILES_EXPIRES = 1
ICAFILESPIPELINE_FILES_EXPIRES = 1
NATIONWIDEFILESPIPELINE_FILES_EXPIRES = 1
MARSHFILESPIPELINE_FILES_EXPIRES = 1

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
