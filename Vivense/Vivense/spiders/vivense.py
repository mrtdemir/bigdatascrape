import scrapy
import json
from scrapy.exceptions import CloseSpider
from scrapy import signals

class VivenseSpider(scrapy.Spider):
    name = 'vivense'
    allowed_domains = ['www.vivense.com']
    start_urls = ['https://www.vivense.com/']
    def __init__(self):
        self.product_dict = dict()
        self.product_category = ""

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs): #implement spider_closed as a super class.
        spider = super(VivenseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self): #Append all data to Json when spider closed.
        with open('products.json', 'w', encoding='utf8') as output:
            json.dump(self.product_dict, output, ensure_ascii=False)
        
    def parse(self,reponse): 
        all_urls = reponse.xpath('//*[@class="subcategory_name"]') #Scrape all all_urls
        for alt_url in all_urls:
            url = alt_url
            url = "https://www.vivense.com"+alt_url.xpath('@href').extract_first()
            url = url.replace('?ref=menu_text',"")
            request = scrapy.Request(
                url, callback=self.parse_first) #Start alt url scrapes.
            yield request

    def parse_first(self, response):

        page_count = response.xpath('//*[@id="search-body"]/div/div/ul/li[last()]/a/text()').extract_first() #Count the pages from navigation.
        if page_count == None or page_count == "":
            page_count = 1
        for i in range(1,int(page_count)+1):    
            absolute_url = response.urljoin(response.url+"?page="+str(i))
            request = scrapy.Request(
                absolute_url, callback=self.parse_contractors) #Yield the counted pages.
            yield request

    def parse_contractors(self, response): #Scrape categories
        url_tags = response.xpath('//*[@id="product-list-wrapper"]/div/div/div/div/a')
        
        self.main_category = (response.xpath('//*[@class="breadcrumb_ol"]/li/a/text()').extract())[-1]
        self.main_category = self.main_category.replace(">","")
        self.main_category = self.main_category.lstrip().rstrip()
        self.category = response.xpath('//*[@class="subcategories-title"]/text()').extract_first() 
        self.category = self.category.strip().replace("\n","")
        if self.category == "KOLTUK TAKIMI":
             self.main_category = "Oturma Odası"
        for url_tag in url_tags:
            url = "https://www.vivense.com"+url_tag.xpath('@href').extract_first()
            request = scrapy.Request(
                url, callback=self.parse_last,cb_kwargs={"categories":self.category,"main_category":self.main_category})
            yield request
    
    def parse_last(self,response,categories,main_category):#Start scraping one by one.

        if main_category not in self.product_dict.keys():
            self.product_dict[main_category] = dict()

        if categories not in self.product_dict[main_category].keys():
            self.product_dict[main_category][categories] = dict()
            self.product_dict[main_category][categories]['Ürün Özellikleri'] = dict()

        features = response.xpath('//*[@id="producttables"]/tr')
        for feature in features:
            try: #Check if the the data valid.
                key = feature.xpath('td[1]/text()').extract_first()
                value = feature.xpath('td[2]/text()').extract_first()
                if key == None or key == "":continue
                if key not in self.product_dict[main_category][categories]['Ürün Özellikleri']:
                    self.product_dict[main_category][categories]['Ürün Özellikleri'][key]=list()
                    self.product_dict[main_category][categories]['Ürün Özellikleri'][key].append(value)
                else:
                    if value not in self.product_dict[main_category][categories]['Ürün Özellikleri'][key]:
                        self.product_dict[main_category][categories]['Ürün Özellikleri'][key].append(value)
            except:
                continue
