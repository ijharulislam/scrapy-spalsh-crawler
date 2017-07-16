import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
import csv
import pkgutil

data = []

# csv_file = pkgutil.get_data("shop_crawler", "spiders/sample_21site_utf8.csv")
from pkg_resources import resource_stream, resource_filename
file_handle = resource_filename('shop_crawler', 'spiders/sample_21site_utf8.csv')

with open('%s'%file_handle, 'r') as f:
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
        for url in data:
            global via_regex
            via_regex = [url["via_page_url_regex"]]
            if ';' in via_regex:
                via_regex = via_regex.split(';')
            if via_regex =='Null' or via_regex =='null':
                via_regex = None

            global single_regex
            single_regex = url["single_shop_url_regex"]

            yield SplashRequest(url['shops_root_url'], self.parse, args={'wait': 0.5})

    def parse(self, response):
        if via_regex:
            le = LinkExtractor(allow = [r"%s"%regex for regex in via_regex])
        else:
            le = LinkExtractor()        
        print("tag +++++++++++ tag")
        for link in le.extract_links(response):
            print("link found", link.url)
            # yield scrapy.Request(url=link.url, callback=self.parse_via_page)

    def parse_via_page(self, response):
        print("Via page urls")
        if single_regex:
            le = LinkExtractor(allow= [r"%s"%single_regex])
        else:
            le = LinkExtractor()
        for link in le.extract_links(response):
            print("link found In via pages",link.url)



