import sys
import json
import csv
import re

# Import Scrapy stuff
import scrapy
from scrapy.http import HtmlResponse
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from pkg_resources import resource_filename

from shop_crawler.items import ShopCrawlerItem


#file_name = resource_filename('shop_crawler', 'spiders/sample_21site_utf8.csv')


src = """
function main(splash)
  local url = splash.args.url
  assert(splash:go(url))
  return {
    html = splash:html()
  }
end

"""

class ShopSpider(scrapy.Spider):
    name = "shops"
    http_user = '59cad0345f804f3faf405a087e3faa5d'

    def __init__(self, *args, **kwargs): 
      super(ShopSpider, self).__init__(*args, **kwargs)

      self.shops_root_url = kwargs.get('Shops_root_url')
      via_page_url_regex = kwargs.get('Via_page_url_regex')

      if ";" in via_page_url_regex:
        self.via_page_url_regex = via_page_url_regex.split(';')
      elif not via_page_url_regex:
        self.via_page_url_regex = ["Null"]
      else:
        self.via_page_url_regex = [via_page_url_regex]

      self.single_shop_url_regex = kwargs.get('Single_shop_url_regex')

    def start_requests(self):
        yield SplashRequest(self.shops_root_url, self.parse, endpoint='execute', args={'lua_source': src})

    def parse(self, response):
        response = HtmlResponse(url=self.shops_root_url, body=response.body)
        if self.via_page_url_regex[0] == "Null":
          le = LinkExtractor(allow = [r"%s"%self.single_shop_url_regex])
          for link in le.extract_links(response):
              yield SplashRequest(url=link.url, callback=self.parse_output, meta={'url':link.url})
        else:
            if self.via_page_url_regex:
                le = LinkExtractor(allow = [r"%s"%self.via_page_url_regex[0]])
                for link in le.extract_links(response):
                    yield SplashRequest(url=link.url, callback=self.parse_via_pages, endpoint='execute', args={'lua_source': src})

    def parse_ajax_pages(self, response):
        response = HtmlResponse(url=self.shops_root_url, body=response.body)
        le = LinkExtractor(allow = [r"%s"%self.single_shop_url_regex])
        for link in le.extract_links(response):
            yield SplashRequest(url=link.url, callback=self.parse_output, meta={'url':link.url})
        
    def parse_via_pages(self, response):
        response = HtmlResponse(url=self.shops_root_url, body=response.body)
        if len(self.via_page_url_regex) == 1:
            le = LinkExtractor(allow = [r"%s"%self.single_shop_url_regex])
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_output, meta={'url':link.url}, endpoint='execute', args={'lua_source': src})
        if len(self.via_page_url_regex) == 2:
            le = LinkExtractor(allow = [r"%s"%self.via_page_url_regex[1]])
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_single_page, meta={'url':link.url}, endpoint='execute', args={'lua_source': src})
        if len(self.via_page_url_regex) == 3:
            le = LinkExtractor(allow = [r"%s"%regex for regex in self.via_page_url_regex])
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_multiple_via_pages, meta={'url':link.url}, endpoint='execute', args={'lua_source': src})

    def parse_multiple_via_pages(self, response):
        response = HtmlResponse(url=self.shops_root_url, body=response.body)
        le = LinkExtractor(allow = [r"%s"%regex for regex in self.via_page_url_regex])
        for link in le.extract_links(response):
                yield scrapy.Request(url=link.url, callback=self.parse_single_page)

    def parse_single_page(self, response):
        response = HtmlResponse(url=self.shops_root_url, body=response.body)
        le = LinkExtractor(allow = [r"%s"%self.single_shop_url_regex])
        for link in le.extract_links(response):
            yield SplashRequest(url=link.url, callback=self.parse_output, meta={'url':link.url})

    def parse_output(self, response):
            url = response.meta.get('url')
            title = response.css('title::text').extract_first()
            if title:
                yield ShopCrawlerItem(title=title.strip(), url=url)



