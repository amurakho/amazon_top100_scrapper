# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from scrappers.items import LinkItem, ErrorItem
from scrapy.exceptions import CloseSpider
import random

from scrappers.utils.manage_db import ManageDB


class GetLinksSpider(scrapy.Spider):
    name = 'get_links'
    allowed_domains = ['amazon.com']
    start_urls = ['http://amazon.com/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'scrappers.pipelines.GetLinkPipeline': 300,
        },
        'DOWNLOAD_DELAY': 0.5,
    }

    def parse(self, response):
        self.manage = ManageDB()
        categories = self.manage.get_n_categories(10, 'new')

        if not categories:
            raise CloseSpider('No more categories')

        for category in categories:
            category_id = category['category_id']
            url = category['url']
            self.manage.change_category_status(category_id, 'processed')
            yield scrapy.Request(url, callback=self.parse_page, meta={'category_id': category_id})
        yield scrapy.Request(url='https://www.example.com',
                             dont_filter=True)

    def parse_page(self, response):
        # if error change user agent and retry
        error_text = response.xpath('//p[@class="a-last"]/text()').get()
        if error_text == "Sorry, we just need to make sure you're not a robot. " \
                         "For best results, please make sure your browser is accepting cookies.":

            user_agent = random.choice(self.settings.get('USER_AGENTS'))
            yield scrapy.Request(url=response.url, callback=self.parse,
                                 headers={'User-Agent': user_agent},
                                 dont_filter=True, meta=response.meta)

        else:
            category_id = response.meta.get('category_id')

            # if cannt find products from category
            blocks = response.css('.zg-item')
            if not blocks:
                item = ErrorItem()
                item['url'] = response.url
                item['category_id'] = category_id
                item['error_text'] = 'Cannt get products from category'
                yield item

            else:
                item = LinkItem()
                item['category_id'] = category_id

                for block in blocks:
                    item['url'] = block.xpath('a[@class="a-link-normal"]/@href').get()
                    yield item
                else:
                    self.manage.change_category_status(category_id, status='done')

                # pagination
                next_page = response.css('.a-last a::attr(href)').get()
                if next_page:
                    yield scrapy.Request(url=next_page, callback=self.parse, meta={
                        'category_id': category_id,
                    })


