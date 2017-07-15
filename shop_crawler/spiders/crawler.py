import scrapy
from scrapy.linkextractors import LinkExtractor


shop_root_url = 'https://www.saint-marc-hd.com/b/saintmarc/?brand_type=CFE'
via_page_url_regex = 'b/saintmarc/attr/\?kencode=(\d+)&brand_type=CFE'
single_shop_url_regex = '/b/saintmarc/info/(¥d+)/?brand_type=CFE'

class ShopSpider(scrapy.Spider):
    name = "shops"

    def start_requests(self):
        urls = [
            shop_root_url
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        le = LinkExtractor(allow=[r"%s"%via_page_url_regex]) # empty for getting everything, check different options on documentation        
        print("tag +++++++++++ tag")
        print(response)
        for link in le.extract_links(response):
            print("link found",link)