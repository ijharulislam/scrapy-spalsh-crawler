import csv
import re
import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from pkg_resources import resource_filename
from shop_crawler.items import ShopCrawlerItem
import sys
import json

file_name = resource_filename('shop_crawler', 'spiders/sample_21site_utf8.csv')


class ShopSpider(scrapy.Spider):
    name = "shops"
    http_user = '59cad0345f804f3faf405a087e3faa5d'

    def __init__(self, *args, **kwargs): 
      super(ShopSpider, self).__init__(*args, **kwargs)

      self.shops_root_url = kwargs.get('Shops_root_url')
      self.via_page_url_regex = kwargs.get('Via_page_url_regex')
      self.single_shop_url_regex = kwargs.get('Single_shop_url_regex')

    def start_requests(self):
        yield scrapy.Request(self.shops_root_url, self.parse, meta={'root_url': self.shops_root_url, 'via_regex': self.via_page_url_regex, 'single_regex': self.single_shop_url_regex})

    # def start_requests(self):
    #     for shop in data:
    #         # yield SplashRequest(shop['shops_root_url'], self.parse, meta={'via_regex': shop["via_page_url_regex"], 'single_regex':shop["single_shop_url_regex"]})
    #         yield scrapy.Request(shop['shops_root_url'], self.parse, meta={'via_regex': shop["via_page_url_regex"], 'single_regex':shop["single_shop_url_regex"]})

    def parse(self, response):
        via_regex = response.meta.get('via_regex')
        if ';' in via_regex:
            via_regex = via_regex.split(';')
        else:
            via_regex = [via_regex]

        single_regex = response.meta.get('single_regex')

        le = LinkExtractor(allow =(), attrs='onclick')
        links = [link.url for link in le.extract_links(response)]
        if len(links) <0:
            yield SplashRequest(self.shops_root_url, self.parse_onclick_pages, endpoint='execute', args={'lua_source': script},  meta={'via_regex': self.via_page_url_regex, 'single_regex': self.single_shop_url_regex})
        else:
            if via_regex[0] == "Null":
                le = LinkExtractor(allow = [r"%s"%single_regex])
                for link in le.extract_links(response):
                    yield SplashRequest(url=link.url, callback=self.parse_output, meta={'url':link.url})
            else:
                if len(via_regex)>0:
                    le = LinkExtractor(allow = [r"%s"%via_regex[0]])
                    for link in le.extract_links(response):
                        yield SplashRequest(url=link.url, callback=self.parse_via_pages, meta={'single_regex':single_regex, 'via_regex':via_regex})          

    def parse_via_pages(self, response):
        single_regex = response.meta.get('single_regex')
        via_regex = response.meta.get('via_regex')
        if len(via_regex) == 1:
            le = LinkExtractor(allow = [r"%s"%single_regex])
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_output, meta={'url':link.url, 'single_regex':single_regex})
        if len(via_regex) == 2:
            le = LinkExtractor(allow = [r"%s"%via_regex[1]])
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_single_page, meta={'url':link.url, 'single_regex':single_regex, 'via_regex':via_regex})
        if len(via_regex) == 3:
            le = LinkExtractor(allow = [r"%s"%regex for regex in via_regex])
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_multiple_via_pages, meta={'url':link.url, 'single_regex':single_regex, 'via_regex':via_regex})

    def parse_multiple_via_pages(self, response):
        single_regex = response.meta.get('single_regex')
        via_regex = response.meta.get('via_regex')
        le = LinkExtractor(allow = [r"%s"%regex for regex in via_regex])
        for link in le.extract_links(response):
                yield scrapy.Request(url=link.url, callback=self.parse_single_page, meta={'url':link.url, 'single_regex':single_regex, 'via_regex':via_regex})

    def parse_single_page(self, response):
        single_regex = response.meta.get('single_regex')
        le = LinkExtractor(allow = [r"%s"%single_regex])
        for link in le.extract_links(response):
            yield SplashRequest(url=link.url, callback=self.parse_output, meta={'url':link.url, 'single_regex':single_regex})

    def parse_output(self, response):
            url = response.meta.get('url')
            title = response.css('title::text').extract_first()
            if title:
                yield ShopCrawlerItem(title=title.strip(), url=url)



