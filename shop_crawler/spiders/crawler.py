import csv
import re
import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from pkg_resources import resource_filename
from shop_crawler.items import ShopCrawlerItem
import sys

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
        single_regex = response.meta.get('single_regex')
        if via_regex == "Null":
            print('via regex single page', via_regex, type(via_regex), via_regex == "Null")
            le = LinkExtractor(allow = [r"%s"%single_regex])
            for link in le.extract_links(response):
                yield scrapy.Request(url=link.url, callback=self.parse_single_page, meta={'url':link.url})
        else:
            print("via pages")
            if ';' in via_regex:
                via_regex = via_regex.split(';')
            else:
                via_regex = [via_regex]
                
            if len(via_regex)>0:
                le = LinkExtractor(allow = [r"%s"%regex for regex in via_regex])
                for link in le.extract_links(response):
                    yield scrapy.Request(url=link.url, callback=self.parse_via_pages, meta={'single_regex':single_regex})
    
    def parse_via_pages(self, response):
        single_regex = response.meta.get('single_regex')
        if single_regex:
            le = LinkExtractor(allow = [r"%s"%single_regex])
            for link in le.extract_links(response):
                yield scrapy.Request(url=link.url, callback=self.parse_single_page, meta={'url':link.url})

    def parse_single_page(self, response):
            url = response.meta.get('url')
            title = response.css('title::text').extract_first()
            yield ShopCrawlerItem(title=title.strip(), url=url)



