import scrapy
from scrapy.linkextractors import LinkExtractor


class ShopSpider(scrapy.Spider):
    name = "shops"

    def start_requests(self):
        urls = [
            'https://www.saint-marc-hd.com/b/saintmarc/?brand_type=CFE'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        le = LinkExtractor() # empty for getting everything, check different options on documentation        
        print("tag +++++++++++ tag")
        print(response)
        for link in le.extract_links(response):
            print("link found",link)