# -*- coding: utf-8 -*-
import scrapy


class GetLinksSpider(scrapy.Spider):
    name = 'get_links'
    allowed_domains = ['amazon.com']
    start_urls = ['http://amazon.com/']

    def parse(self, response):
        pass
