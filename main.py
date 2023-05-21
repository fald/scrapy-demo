# Scrapy boilerplate
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

# Import item that will be used to generate JSON feed
from crawler.items import CrawlerItem

# Import helper functions
from crawler.helpers import *



if __name__ == "__main__":
    pass
