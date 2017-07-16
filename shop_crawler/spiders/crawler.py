import csv
import re
import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from pkg_resources import resource_filename

file_name = resource_filename('shop_crawler', 'spiders/sample_21site_utf8.csv')

data = []

with open('%s'%file_name, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_data = {
                'shops_root_url': row['Shops_root_url'],
                'via_page_url_regex': row['Via_page_url_regex'],
                'single_shop_url_regex': row['Single_shop_url_regex']
            }
            data.append(raw_data)


class ShopSpider(scrapy.Spider):
    name = "shops"
    http_user = '59cad0345f804f3faf405a087e3faa5d'

    def start_requests(self):
        for shop in data:
            yield SplashRequest(shop['shops_root_url'], self.parse, args={'wait': 0.5}, meta={'via_regex': shop["via_page_url_regex"], 'single_regex':shop["single_shop_url_regex"]})

    def parse(self, response):
        via_regex = response.meta.get('via_regex')
        if ';' in via_regex:
                via_regex = via_regex.split(';')
        if via_regex == 'Null' or via_regex =='null' or not via_regex:
            via_regex = None
        else:
            via_regex = [via_regex]
        single_regex = response.meta.get('single_regex')

        if via_regex is not None and len(via_regex)>0:
            le = LinkExtractor(allow = [r"%s"%regex for regex in via_regex])
        else:
            le = LinkExtractor()       
        print("tag +++++++++++ tag")
        for link in le.extract_links(response):
            match = re.search(r'%s'%single_regex, link.url)
            if match:
                print(single_regex, match.group())
                yield scrapy.Request(url=link.url, callback=self.parse_single_page, meta={'url':link.url})

    def parse_single_page(self, response):
            url = response.meta.get('url')
            title = response.css('title::text').extract_first()
            print("Single Page Title", url, title)



