import scrapy
import random
from bookscraper.items import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]
    
    custom_settings = {
        "FEEDS": {
            "latest.json": {"format": "json", 'overwrite': True}
        }
    }
    
    # # Naturally want these to be distinct in a real application
    # user_agent_list = [
    #     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    #     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    #     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    #     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    #     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    # ]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            # This just gives you a generator of all the books and their urls
            # yield {
            #     'name': book.css("h3 a::text").get(),
            #     'price': book.css(".product_price .price_color::text").get(),
            #     'url': book.css("h3 a").attrib["href"]
            # }
            
            # This instead grabs each book's url and then follows it with the different callback.
            # What to do with each book when scraped from the catalogue.
            relative_url = book.css("h3 a").attrib["href"]
            if 'catalogue/' in relative_url:
                book_url = "http://books.toscrape.com/" + relative_url
            else:
                book_url = "http://books.toscrape.com/catalogue/" + relative_url
            # Not parsing the results pages with these, so we want a separate parser.
            yield response.follow(book_url, callback=self.parse_book_page)
            
        # This takes the next page buttons, follows them with the same parse method,
        # then adds the result to the yielded generator.
        next_page = response.css("li.next a").attrib['href']
        if next_page:
            next_url = "http://books.toscrape.com/"
            if 'catalogue/' in next_page:
                next_url += next_page
            else:
                next_url += "catalogue/" + next_page
            yield response.follow(next_url, callback=self.parse)
            
    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        book_item = BookItem()
        
        # This way doesn't make use of items
        # yield {
        #     'url': response.url,
        #     'title': response.css('.product_main h1::text').get(),
        #     'star_rating': response.css("p.star-rating").attrib['class'],
        #     'price': response.css("p.price_color ::text").get(),
        #     'product_type': table_rows[1].css("td ::text").get(),
        #     'price_excl_tax': table_rows[2].css("td ::text").get(),
        #     'price_incl_tax': table_rows[3].css("td ::text").get(),
        #     'tax': table_rows[4].css("td ::text").get(),
        #     'availability': table_rows[5].css("td ::text").get(),
        #     'num_reviews': table_rows[6].css("td ::text").get(),
        #     'category': response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        #     'description': response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
        # }
        
        # This way does        
        book_item["url"] = response.url
        book_item["title"] = response.css('.product_main h1::text').get()
        book_item["star_rating"] = response.css("p.star-rating").attrib['class']
        book_item["price"] = response.css("p.price_color ::text").get()
        book_item["product_type"] = table_rows[1].css("td ::text").get()
        book_item["price_excl_tax"] = table_rows[2].css("td ::text").get()
        book_item["price_incl_tax"] = table_rows[3].css("td ::text").get()
        book_item["tax"] = table_rows[4].css("td ::text").get()
        book_item["availability"] = table_rows[5].css("td ::text").get()
        book_item["num_reviews"]= table_rows[6].css("td ::text").get()
        book_item["category"] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        book_item["description"] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
        
        yield book_item
