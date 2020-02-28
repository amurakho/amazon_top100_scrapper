# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from scrappers.items import LinkItem, ErrorItem
from scrappers.utils.manage_db import ManageDB
from scrapy.exceptions import CloseSpider
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

    def parse(self, response):
        # self.manage = ManageDB()
        # categories = self.manage.get_n_links(10, 'new')
        categories = [(12, 'Any Department/Cell Phones & Accessories', 'https://www.amazon.com/Best-Sellers/zgbs/wireless/ref=zg_bs_nav_0/134-5631722-2954113', 'new', 2), (13, 'Any Department/Camera & Photo', 'https://www.amazon.com/best-sellers-camera-photo/zgbs/photo/ref=zg_bs_nav_0/134-5631722-2954113', 'new', 2), (14, 'Any Department/CDs & Vinyl', 'https://www.amazon.com/best-sellers-music-albums/zgbs/music/ref=zg_bs_nav_0/134-5631722-2954113', 'new', 2), (15, 'Any Department/Baby', 'https://www.amazon.com/Best-Sellers-Baby/zgbs/baby-products/ref=zg_bs_nav_0/134-5631722-2954113', 'new', 2), (16, 'Any Department/Books', 'https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_nav_0/134-5631722-2954113', 'new', 2), (17, 'Any Department/Beauty & Personal Care', 'https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/ref=zg_bs_nav_0/134-5631722-2954113', 'new', 2), (18, 'Any Department/Automotive', 'https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/ref=zg_bs_nav_0/134-5631722-2954113', 'new', 2), (19, 'Any Department/Handmade Products/Health & Personal Care', 'https://www.amazon.com/Best-Sellers-Handmade-Health-Personal-Care-Products/zgbs/handmade/19530416011/ref=zg_bs_nav_hnd_1_hnd', 'new', 3), (20, 'Any Department/Coin Sets', 'https://www.amazon.com/Best-Sellers-Collectible-Coins-Coin-Sets/zgbs/coins/9003136011/ref=zg_bs_nav_coins_col_1_coins_col', 'new', 2), (21, 'Any Department/Handmade Products/Clothing, Shoes & Accessories', 'https://www.amazon.com/Best-Sellers-Handmade-Clothing-Shoes-Accessories/zgbs/handmade/17714704011/ref=zg_bs_nav_hnd_1_hnd', 'new', 3)]

        if not categories:
            raise CloseSpider('No more categories')

        for category in categories:
            category_id = category[0]
            url = category[2]
            # self.manage.change_category_status(category_id, 'processed')
            yield scrapy.Request(url, callback=self.parse_page, meta={'category_id': category_id})
            break

        # yield scrapy.Request(url='https://www.example.com',
        #                      dont_filter=True)

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
                    break
                else:
                    self.manage.change_category_status(category_id, status='done')

                # # pagination
                # next_page = response.css('.a-last a::attr(href)').get()
                # if next_page:
                #     yield scrapy.Request(url=next_page, callback=self.parse, meta={
                #         'category_id': category_id,
                #     })


