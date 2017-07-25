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

script = """
treat = require("treat")
function main(splash)
  local url = splash.args.url
  local link_index = splash.args.link_index
  assert(splash:go(url))
  local links = splash:select_all('a')
  local results = {}
  for i, v in ipairs( links ) do
    if i == link_index then
        obj = {}
        links[link_index]:click()
        splash:wait(5)
        obj["html"] = splash:html()
        obj["url"] = splash:evaljs("window.location.href")
        obj["title"] = splash:evaljs("document.title")
        results[#results+1] = obj
    end
  end
  return {
    results = treat.as_array(results),
  }
end
"""

class ShopSpider(scrapy.Spider):
    name = "onclick_shops"
    http_user = '59cad0345f804f3faf405a087e3faa5d'

    def __init__(self, *args, **kwargs): 
      super(ShopSpider, self).__init__(*args, **kwargs)

      self.shops_root_url = kwargs.get('Shops_root_url')
      via_page_url_regex = kwargs.get('Via_page_url_regex', 'Null')

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
        all_links = response.xpath('*//a/@href').extract()
        link_index = 0
        for link in all_links:
          print(link)
          link_index = link_index + 1
          yield SplashRequest(url=self.shops_root_url, callback=self.parse_via_pages, endpoint='execute', args={'lua_source': script,'link_index':link_index})
        
    def parse_via_pages(self, response):
        if response.data["results"]:
          res = response.data["results"][0]["html"]
          url = response.data["results"][0]["url"]
          title = response.data["results"][0]["title"]
          print("URL:", url)
          response = HtmlResponse(url=self.shops_root_url, body=response.body)

          if self.via_page_url_regex == "Null":
            match = re.search(r'%s'%self.single_shop_url_regex, url)
            if match:
              yield ShopCrawlerItem(title=title.strip(), url=url)

          elif len(self.via_page_url_regex) == 1:
              match = re.search(r'%s'%self.via_page_url_regex[0], url)
              if match:
                le = LinkExtractor(allow =())
                link_index = 0
                for link in le.extract_links(response):
                  link_index = link_index + 1
                  yield SplashRequest(url=link.url, callback=self.parse_single_page, endpoint='execute', args={'lua_source': script,'link_index':link_index})

          if len(self.via_page_url_regex) == 2:
            match = re.search(r'%s'%self.via_page_url_regex[0], url)
            print("match:", match)
            if match:
              all_links = response.xpath('*//a/@href').extract()
              link_index = 0
              for link in all_links:
                link_index = link_index + 1
                # match = re.search(r'%s'%self.via_page_url_regex[1], link)
                # if match:
                yield SplashRequest(url=url, callback=self.parse_second_via_page, endpoint='execute', args={'lua_source': script,'link_index':link_index})
        
    def parse_second_via_page(self, response):
        if response.data["results"]:
          res = response.data["results"][0]["html"]
          url = response.data["results"][0]["url"]
          response = HtmlResponse(url=self.shops_root_url, body=response.body)
          match = re.search(r'%s'%self.via_page_url_regex[1], url)
          if match:
            all_links = response.xpath('*//a/@href').extract()
            print("All link from second level", all_links)
            link_index = 0
            for link in all_links:
              print("Link from second page", link)
              link_index = link_index + 1
              if "p/shopmap/dtl" in link:
                yield SplashRequest(url=url, callback=self.parse_single_page, endpoint='execute', args={'lua_source': script,'link_index':link_index})


    def parse_single_page(self, response):
        if response.data["results"]:
          res = response.data["results"][0]["html"]
          url = response.data["results"][0]["url"]
          title = response.data["results"][0]["title"]
          
          # match = re.search(r'%s'%self.single_shop_url_regex, url)
          # if match:
          print("URL parse_single_page", url)
          if "p/shopmap/dtl" in url:
            print("Last Page URL", url)
            yield ShopCrawlerItem(title=title.strip(), url=url)
