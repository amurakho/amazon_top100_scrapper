# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
from scrappers.items import LinkItem, ErrorItem
from scrappers.utils.manage_db import ManageDB

class GetLinkPipeline():

    @staticmethod
    def _get_asin(url):
        return url[url.find('dp/') + 3:url.find('?')]

    def process_item(self, item, spider):
        manage = ManageDB()
        # if was error
        if isinstance(item, ErrorItem):
            manage.insert_error(item)
        else:
            item['asin'] = self._get_asin(item['url'])
            manage.insert_link(item)
        return item


class GetCategoryPipeline():

    def process_item(self, item, spider):
        if item['name'] == 'Any Department':
            return item
        manage = ManageDB()
        manage.insert_category(item)
        return item