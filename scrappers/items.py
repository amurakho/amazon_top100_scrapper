# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CategoryItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class LinkItem(scrapy.Item):
    url = scrapy.Field()
    category = scrapy.Field()


class ErrorItem(scrapy.Item):
    url = scrapy.Field()
    error_text = scrapy.Field()
    category = scrapy.Field()