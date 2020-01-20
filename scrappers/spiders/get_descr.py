# -*- coding: utf-8 -*-
import scrapy


class GetDescrSpider(scrapy.Spider):
    name = 'get_descr'
    allowed_domains = ['amazon.com']
    start_urls = ['http://amazon.com/']

    def parse(self, response):
        pass
