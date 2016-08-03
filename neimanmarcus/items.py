# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NeimanmarcusItem(scrapy.Item):
    # define the fields for your item here like:
    # sku = scrapy.Field()    
    im_name = scrapy.Field()
    im_url = scrapy.Field()
    product_id = scrapy.Field()
    product_url = scrapy.Field()    
    brand_name = scrapy.Field()
    product_name = scrapy.Field()    
    price = scrapy.Field()
    currency = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    gender = scrapy.Field()
    store = scrapy.Field()
    description = scrapy.Field()
    im_url_small = scrapy.Field()
    im_url_md = scrapy.Field()
    im_url_display = scrapy.Field()
    #For downloading images    
    # images = scrapy.Field()
    # image_urls = scrapy.Field()
    
    
