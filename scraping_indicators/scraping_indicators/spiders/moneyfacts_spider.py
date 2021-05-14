import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import json
import pandas as pd
from scraping_indicators.items import MoneyFactsItem
from scraping_indicators.settings import end_of_prev_mth, end_of_prev_mth_file_string, FILES_STORE

# only scrape the first to buy mortgage rates for 2yr and 5yr
# only look at LVR of 75
# raw data can be scraped as json. This is saved in a separate file in the moneyfacts directory
# the data to be be used in the dashboard is parsed separately from the raw data - only certain fields are used
# csv file containing the rates history from CS and data scraped going forward is in the data directory

class MoneyfactsSpider(scrapy.Spider):
    name = 'moneyfacts'
    custom_settings = {
        'ITEM_PIPELINES': {'scraping_indicators.pipelines.MoneyfactsPipeline': 300},
        # 'FEEDS': {
        #     'file:///' + FILES_STORE + '\\moneyfacts.csv': {
        #         'format': 'csv',
        #         'fields': ['Date', 'Id', 'Term', 'Company', 'Rate', 'LTV', 'IsFirstTimeBuyer', 'IsRemortgage'],
        #     },
        # }
    }

    # selenium only works when there is one start url because the requests are asynchronous
    # subsequent urls need to be requested in the callback function
    urls = [
        'https://moneyfacts.co.uk/mortgages/your-results/?id=null&buyer-type=8&amount-to-borrow=150000&property-value=200000&repayment-type=1&term=25&mortgage-types=1&initial-rate-periods=16&region=16&payable-over-period=8&refinements=null'
    ]
    url_index = 0

    # only want to click the notification button once
    notification_click = False

    def start_requests(self):
        start_url = 'https://moneyfacts.co.uk/mortgages/your-results/?id=null&buyer-type=8&amount-to-borrow=150000&property-value=200000&repayment-type=1&term=25&mortgage-types=1&initial-rate-periods=2&region=16&payable-over-period=2&refinements=null'
        yield SeleniumRequest(
            url=start_url,
            callback=self.parse_result,
            wait_time=10,
            wait_until=EC.element_to_be_clickable((By.ID, 'show-more'))
        )

    def parse_result(self, response):
        driver = response.request.meta['driver']
        button = driver.find_element_by_xpath("//button[@id='show-more']")
        if not self.notification_click:
            driver.find_element_by_xpath("//button[@id='dismiss-notification-banner']").click()
            self.notification_click = True

        can_click_button = True
        while can_click_button:
            try:
                button.click()
            except ElementNotInteractableException:
                can_click_button = False
                response = scrapy.http.TextResponse(url=driver.current_url, body=driver.page_source, encoding='utf-8')
                data = response.xpath('//@data-product').extract()
                term = '2yr' if self.url_index == 0 else '5yr'

                # code to scrape all the data into a csv
                json_data = []
                for d in data:
                    json_data.append(json.loads(d))

                df = pd.DataFrame.from_records(json_data)
                df.to_csv(FILES_STORE + '\\moneyfacts\\' + end_of_prev_mth_file_string + '_' + term + '.csv')
                df['Term'] = term
                df['Date'] = end_of_prev_mth
                fields = ['Date', 'Id', 'Term', 'Company', 'Rate', 'MaxLTV']
                df = df[fields]
                df['Rate'] = pd.to_numeric(df['Rate'])
                df['MaxLTV'] = pd.to_numeric(df['MaxLTV'])
                df = df[df['MaxLTV'] >= 75]
                df = df.groupby(['Company']).min()
                df = df.reset_index()[fields]

                for index, row in df.iterrows():
                    item = MoneyFactsItem()
                    item['Date'] = row['Date']
                    item['Id'] = row['Id']
                    item['Term'] = row['Term']
                    item['Company'] = row['Company']
                    item['Rate'] = row['Rate']
                    item['MaxLTV'] = row['MaxLTV']

                    yield item

        if self.url_index < len(self.urls):
            yield SeleniumRequest(
                url=self.urls[self.url_index],
                callback=self.parse_result,
                wait_time=10,
                wait_until=EC.element_to_be_clickable((By.ID, 'show-more'))
            )
            self.url_index += 1