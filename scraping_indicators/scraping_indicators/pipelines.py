# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy.exporters import CsvItemExporter
import pandas as pd
from statsmodels.tsa.seasonal import STL
from scraping_indicators.settings import FILES_STORE
from datetime import datetime

data_file = FILES_STORE + '\\data.csv'
moneyfacts_file = FILES_STORE + '\\moneyfacts.csv'
moneyfacts_fields = ['Date', 'Id', 'Term', 'Company', 'Rate', 'MaxLTV']


def update_data_csv(data_col_name, ser):
    """update data csv column with values from the scraped series"""
    data = pd.read_csv(data_file, index_col='Date')
    data.index = pd.to_datetime(data.index)
    data = data.merge(right=ser, how='outer', left_index=True, right_index=True)
    data[data_col_name] = data.iloc[:, -1]
    data = data.iloc[:, :-1]
    data.to_csv(data_file, index_label='Date')


class ApraFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return 'apra_data.xlsx'

    def item_completed(self, results, item, info):
        """open downloaded apra file and calculate commercial avg premium trend,
        open data.csv file and update data"""
        if results[0][0]:
            if results[0][1]['status'] == 'downloaded':
                file = results[0][1]['path']
                df_apra = pd.read_excel(FILES_STORE + '\\' + file, sheet_name='Data', index_col='Reporting date')
                df_apra.index = pd.to_datetime(df_apra.index)
                commercial = ['Commercial motor vehicle', 'Fire and industrial special risks (ISR)',
                              'Public and product liability', 'Professional indemnity', "Employers' liability"]
                items = ['Gross written premium by class of business', 'Number of risks written by class of business']
                df_commercial = df_apra[df_apra['Class of business'].isin(commercial)]
                df_commercial = df_commercial[df_commercial['Data item'].isin(items)]
                df_commercial_grp = df_commercial.groupby([df_commercial.index, 'Data item']).sum().unstack()
                df_commercial_avg_prem = df_commercial_grp[('Value', 'Gross written premium by class of business')] / \
                                         df_commercial_grp[('Value', 'Number of risks written by class of business')]
                df_commercial_avg_prem.dropna(inplace=True)
                res = STL(df_commercial_avg_prem, period=4).fit()
                update_data_csv('commercial_avg_prem_trend', res.trend)

        return item


class IcaFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return 'insurance_council_data.xlsx'

    def item_completed(self, results, item, info):
        """open downloaded ica file, open data.csv file and update data"""
        if results[0][0]:
            if results[0][1]['status'] == 'downloaded':
                file = results[0][1]['path']
                ica_fields = ['Home Building Insurance', 'Home Contents Insurance', 'Comprehensive Motor Vehicle Insurance']
                data_fields = ['home_building_avg_prem_trend', 'home_contents_avg_prem_trend', 'motor_avg_prem_trend']
                df = pd.read_excel(FILES_STORE + '\\' + file)
                for ica_field, data_field in zip(ica_fields, data_fields):
                    ica_idx = df.columns.get_loc(ica_field)
                    ser = df.iloc[:, ica_idx:ica_idx + 2]
                    ser.dropna(inplace=True)
                    ser = ser.iloc[1:, :]
                    ser.columns = ['Date', ica_field]
                    ser['Date'] = pd.to_datetime(ser['Date'])
                    ser['Date'] = ser['Date'].apply(lambda x: x + pd.DateOffset(months=1) - pd.DateOffset(days=1))
                    ser.set_index('Date', inplace=True)
                    ser = ser.iloc[:, 0]
                    update_data_csv(data_field, ser)


class MoneyfactsPipeline(object):

    def open_spider(self, spider):
        self.file = open(moneyfacts_file, 'ab')
        self.exporter = CsvItemExporter(file=self.file, include_headers_line=False)
        self.exporter.fields_to_export = moneyfacts_fields

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.start_exporting()
        self.exporter.export_item(item)

        return item


class NationwideFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return 'nationwide_uk_housing.xls'

    def item_completed(self, results, item, info):
        """open downloaded file, open data.csv file and update data"""
        if results[0][0]:
            if results[0][1]['status'] == 'downloaded':
                file = results[0][1]['path']
                df = pd.read_excel(FILES_STORE + '\\' + file, index_col=0)
                ser = df.loc['Q1 2016':,'Seasonally Adjusted Index:']
                months = pd.date_range(start='31/3/2016', end=datetime.today(), freq='3M')
                months = months[:ser.shape[0]]
                ser.index = months
                update_data_csv('uk_housing_index', ser)


class MarshFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return 'marsh_global_commercial_insurance.xlsx'

    def item_completed(self, results, item, info):
        """open downloaded file, open data.csv file and update data"""
        if results[0][0]:
            if results[0][1]['status'] == 'downloaded':
                file = results[0][1]['path']
                marsh_fields = ['US Insurance Composite Renewal Rate', 'UK Insurance Composite Renewal Rate ', 'Continental Europe Insurance Composite Renewal Rate']
                data_fields = ['us_commercial_pricing_trend', 'uk_commercial_pricing_trend', 'eu_commercial_pricing_trend']
                df = pd.read_excel(FILES_STORE + '\\' + file, index_col=0)
                for marsh_field, data_field in zip(marsh_fields, data_fields):
                    ser = df[marsh_field]
                    months = pd.date_range(start='31/12/2013', end=datetime.today(), freq='3M')
                    months = months[:ser.shape[0]]
                    ser.index = months
                    data = pd.read_csv(data_file, index_col='Date')
                    data.index = pd.to_datetime(data.index)
                    data.loc[ser.index[-1], data_field] = data.loc[ser.index[-2], data_field] * (1 + ser[-1])
                    data.to_csv(data_file)