# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class NeimanmarcusPipeline(object):
    def process_item(self, item, spider):
        return item

# import scrapy
# from scrapy.contrib.pipeline.images import ImagesPipeline
# from scrapy.exceptions import DropItem

# class MyImagesPipeline(ImagesPipeline):

#     def image_key(self, url):
#         image_guid = url.split('/')[-1]
#         return 'images/%s' % (image_guid)

#     def get_media_requests(self, item, info):
#         for image_url in item['image_urls']:
#             yield scrapy.Request(image_url)
