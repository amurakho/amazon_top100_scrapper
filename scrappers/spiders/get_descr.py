# -*- coding: utf-8 -*-
import scrapy


class GetDescrSpider(scrapy.Spider):
    name = 'get_descr'
    allowed_domains = ['amazon.com']
    start_urls = ['http://amazon.com/']

    def parse(self, response):
        self.manage = ManageDB()
        categories = self.manage.get_n_links(10, 'new')

        if not categories:
            raise CloseSpider('No more categories')
