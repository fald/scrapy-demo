import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            # This just gives you a generator of all the books and their urls
            # yield {
            #     'name' : book.css("h3 a::text").get(),
            #     'price' : book.css(".product_price .price_color::text").get(),
            #     'url' : book.css("h3 a").attrib["href"]
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
        pass
