# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Strip whitespace from non-description strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                if type(value) is tuple:
                    value = value[0]
                adapter[field_name] = value.strip()
                
        # Make field lowercase for standardization.
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()
            
        # Remove currency sign and convert to float
        price_keys = ["price", "price_incl_tax", "price_excl_tax", "tax"]
        for price_key in price_keys:
            value = adapter.get(price_key)
            adapter[price_key] = float(value.replace("£", ""))
            
        # Convert availability text to number in stock
        value = adapter.get('availability')
        split = value.split("(")
        if len(split) < 2: # not formatted like everything else in stock
            adapter['availability'] = 0
        else:
            adapter['availability'] = int(split[1].split(" ")[0])
            
        # Straightforward conversion of str -> int
        value = adapter.get("num_reviews")
        adapter['num_reviews'] = int(value)
        
        # Convert star ratings to ints
        value = adapter.get("star_rating")
        ratings = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5
        }
        adapter["star_rating"] = ratings[value.split(" ")[1].lower()]
         
        return item
    

class SaveToPostgresPipeline:
    def __init__(self):
        self.conn = psycopg2.connect(
            host = "localhost",
            database = "books",
            user = "postgres",
            password = "password"
        )
        
        # Create cursor to execute commands
        self.cur = self.conn.cursor()
        
        # Create book table (to go into the books db, I am a naming genius.)
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                url VARCHAR(255),
                title text,
                product_type VARCHAR(255),
                price DECIMAL,
                price_excl_tax DECIMAL,
                price_incl_tax DECIMAL,
                tax DECIMAL,
                availability int,
                num_reviews int,
                star_rating int,
                category VARCHAR(255),
                description text
            );
            """
        )
                
    def process_item(self, item, spider):
        self.cur.execute(
            """
            INSERT INTO books (
                url,
                title,
                product_type,
                price,
                price_incl_tax,
                price_excl_tax,
                tax,
                availability,
                num_reviews,
                star_rating,
                category, 
                description
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                item['url'],
                item['title'],
                item['product_type'],
                item['price'],
                item['price_incl_tax'],
                item['price_excl_tax'],
                item['tax'],
                item['availability'],
                item['num_reviews'],
                item['star_rating'],
                item['category'],
                item['description']
            )
        )
        
        self.conn.commit()
        return item
        
    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
