# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from scrappers.items import LinkItem, ErrorItem
import random


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

    def start_requests(self):
        df = pd.read_csv('category_base.csv')
        for _, row in df.iterrows():
            category = row['name']
            url = row['url']

            url = 'https://www.amazon.com/Best-Sellers-Amazon-Devices/zgbs/amazon-devices/2102313011/ref=zg_bs_nav_1_amazon-devices'
            yield scrapy.Request(url, callback=self.parse, meta={'category': category})
            break

    def parse(self, response):
        # if error change user agent and retry
        error_text = response.xpath('//p[@class="a-last"]/text()').get()
        if error_text == "Sorry, we just need to make sure you're not a robot. " \
                         "For best results, please make sure your browser is accepting cookies.":

            user_agent = random.choice(self.settings.get('USER_AGENTS'))
            yield scrapy.Request(url=response.url, callback=self.parse,
                                 headers={'User-Agent': user_agent},
                                 dont_filter=True, meta=response.meta)

        else:
            category = response.meta.get('category')

            # if cannt find products from category
            blocks = response.css('.zg-item')
            if not blocks:
                item = ErrorItem()
                item['url'] = response.url
                item['category'] = category
                item['error_text'] = 'Cannt get products from category'
                yield item

            item = LinkItem()
            item['category'] = category

            for block in blocks:
                item['url'] = block.xpath('a[@class="a-link-normal"]/@href').get()
                yield item
                break

            # pagination
            next_page = response.css('.a-last a::attr(href)').get()
            if next_page:
                yield scrapy.Request(url=next_page, callback=self.parse, meta={
                    'category': category,
                })
