# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
from scrappers.items import LinkItem, ErrorItem
import mysql.connector

class GetLinkPipeline(object):

    @staticmethod
    def _get_asin(url):
        return url[url.find('dp/') + 3:url.find('?')]

    def _connect(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='amazon_links',
            passwd='utor93lol',
            database='amazon_links'
        )
        self.curr = self.conn.cursor()

    def _create_table(self):
        # error table
        self.curr.execute(
            """
                CREATE TABLE IF NOT EXISTS errors (
                    error_id int unsigned not null auto_increment,
                    text text,
                    url text,
                    category text,
                    PRIMARY KEY(error_id)
                    );
            """
        )

        # links table
        self.curr.execute(
            """
                CREATE TABLE IF NOT EXISTS links (
                    link_id int unsigned not null auto_increment,
                    category text,
                    url text,
                    asin VARCHAR(15)
                    PRIMARY KEY(link_id)
                    );
            """
        )

    def process_item(self, item, spider):
        self._connect()
        self._create_table()
        # if was error
        if isinstance(item, ErrorItem):
            self.curr.execute(
                """
                INSERT INTO errors(url, text, category)
                VALUES (%s, %s, %s)
                """,
                item['url'],
                item['error_text'],
                item['category']
            )
        else:
            asin = self._get_asin(item['url'])
            self.curr.execute(
                """
                INSERT INTO links(url, category, asin)
                VALUES (%s, %s, %s)
                """,
                item['url'],
                item['category'],
                asin
            )
        return item
