# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from urllib.parse import urlencode
from random import choice
import requests
import base64


class BookscraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BookscraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapeOpsFakeUserAgentMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def __init__(self, settings):
        self.scrapeops_api_key = settings.get("SCRAPEOPS_API_KEY")
        self.scrapeops_endpoint = settings.get("SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT", "https://headers.scrapeops.io/v1/user-agents")
        self.scrapeops_fake_user_agents_active = settings.get("SCRAPEOPS_FAKE_USER_AGENTS_ACTIVE", False)
        self.scrapeops_num_results = settings.get("SCRAPEOPS_NUM_RESULTS", 2) # Low default number
        self.headers_list = []
        self._get_user_agents_list()
        self._scrapeops_fake_user_agents_enabled()
        
    def _get_user_agents_list(self):
        payload =  {
            "api_key": self.scrapeops_api_key,
            "num_results": self.scrapeops_num_results
        }
        response = requests.get(
            url=self.scrapeops_endpoint,
            params=urlencode(payload)
        )
        json_response = response.json()
        self.user_agents_list = json_response.get('result', [])
        # print("*"*50, "\n"*10, json_response, "\n"*10, "*"*50)
        
    def _get_random_user_agent(self):
        return choice(self.user_agents_list)
    
    def _scrapeops_fake_user_agents_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key == "":
            self.scrapeops_fake_user_agents_active = False
        else:
            self.scrapeops_fake_user_agents_active = True    
            
    def process_request(self, request, spider):
        random_user_agent = self._get_random_user_agent()
        request.headers['User-Agent'] = random_user_agent
        
        # print("*"*50, "\n"*10, "\nNEW USER AGENT", request.headers["User-Agent"], "\n"*10, "*"*50)


class ScrapeOpsFakeBrowserHeaderAgentMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def __init__(self, settings):
        self.scrapeops_api_key = settings.get("SCRAPEOPS_API_KEY")
        self.scrapeops_endpoint = settings.get("SCRAPEOPS_FAKE_BROWSER_HEADER_ENDPOINT", "https://headers.scrapeops.io/v1/browser-headers")
        self.scrapeops_fake_user_agents_active = settings.get("SCRAPEOPS_FAKE_BROWSER_HEADERS_ACTIVE", True)
        self.scrapeops_num_results = settings.get("SCRAPEOPS_NUM_RESULTS", 2) # Low default number
        self.headers_list = []
        self._get_headers_list()
        self._scrapeops_fake_browser_headers_enabled()
        
    def _get_headers_list(self):
        payload = {
            "api_key": self.scrapeops_api_key,
            "num_results": self.scrapeops_num_results
        }
        response = requests.get(
            url=self.scrapeops_endpoint,
            params=urlencode(payload)
        )
        json_response = response.json()
        self.headers_list = json_response.get('result', [])
        
    def _get_random_browser_header(self):
         return choice(self.headers_list)
    
    def _scrapeops_fake_browser_headers_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key == "":
            self.scrapeops_fake_user_agents_active = False
        else:
            self.scrapeops_fake_user_agents_active = True
            
    def process_request(self, request, spider):
        random_header = self._get_random_browser_header()
        # This is a doozy
        # print("*"*50, "\n"*10, "\nNEW BROWSER HEADER", random_header, "\n"*10, "*"*50)
        request.headers.update(random_header)


class MyProxyMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def __init__(self, settings):
        self.user = settings.get("PROXY_USER")
        self.password = settings.get("PROXY_PASSWORD")
        self.endpoint = settings.get("PROXY_ENDPOINT")
        self.port = settings.get("PROXY_PORT")
    
    def process_request(self, request, spider):
        user_credentials = f"{self.user}:{self.password}"
        basic_authorization = "Basic " + base64.b64encode(user_credentials.encode()).decode()
        request.headers['Proxy-Authorization'] = basic_authorization
        request.meta['proxy'] = f"http://{self.endpoint}:{self.port}"
