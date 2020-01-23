# -*- coding: utf-8 -*-
import scrapy
from scrappers.items import CategoryItem


class AmazonSpider(scrapy.Spider):
    name = 'amazon_categories'
    allowed_domains = ['amazon.com']
    start_urls = ['https://www.amazon.com/Best-Sellers/zgbs/']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrappers.pipelines.GetCategoryPipeline': 300,
        },
        # 'DOWNLOAD_DELAY': 1,
    }

    base_url = 'https://www.amazon.com'

    category_urls = ['https://www.amazon.com/Best-Sellers/zgbs', ]

    def parse(self, response):
        item = CategoryItem()

        blocks = response.xpath('//ul[@id="zg_browseRoot"]')

        categories = blocks.css('.zg_browseUp a::text').getall()
        categories.append(blocks.css('.zg_selected::text').get().strip())
        item['name'] = '/'.join(categories)
        item['url'] = response.url
        item['status'] = 'new'
        yield item

        blocks = blocks.css('a::attr(href)').getall()
        for url in blocks:
            if url not in self.category_urls:
                self.category_urls.append(url)
                yield scrapy.Request(url, callback=self.parse)
