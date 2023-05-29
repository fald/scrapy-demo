import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            yield {
                'name' : book.css("h3 a::text").get(),
                'price' : book.css(".product_price .price_color::text").get(),
                'url' : book.css("h3 a").attrib["href"]
            }
        
        next_page = response.css("li.next").attrib['href'].get()
        if next_page:
            next_url = "http://books.toscrape.com/" + next_page
            yield response.follow(next_url, callback=self.parse)
