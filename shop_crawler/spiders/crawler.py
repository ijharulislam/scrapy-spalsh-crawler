import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor


shop_root_urls = [
        # 'https://www.saint-marc-hd.com/b/saintmarc/?brand_type=CFE',
        'https://map.yoshinoya.com/p/shopmap/',
        # 'http://sasp.mapion.co.jp/b/doutor/?shopmastergyokna=1100',
        # 'https://www.redlobster.com/locations/list'
    ]
via_page_url_regex = ['b/saintmarc/attr/\?kencode=(\d+)&brand_type=CFE']
single_shop_url_regex = '/b/saintmarc/info/(\d+)/?brand_type=CFE'

class ShopSpider(scrapy.Spider):
    name = "shops"

    def start_requests(self):
        urls = shop_root_urls
        
        for url in urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        le = LinkExtractor(attrs=('onclick',),) # empty for getting everything, check different options on documentation        
        #le = LinkExtractor(allow= [r"%s"%regex for regex in via_page_url_regex]) # empty for getting everything, check different options on documentation        
        print("tag +++++++++++ tag")
        print(response)
        for link in le.extract_links(response):
            print("link found",link.url)
            # yield scrapy.Request(url=link.url, callback=self.parse_via_page)

    def parse_via_page(self, response):
        print("Via page urls")
        # le = LinkExtractor(allow= [r"%s"%single_shop_url_regex])
        le = LinkExtractor()
        for link in le.extract_links(response):
            print("link found In via pages",link.url)



