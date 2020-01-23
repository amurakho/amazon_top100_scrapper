# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
from scrappers.items import LinkItem, ErrorItem
from scrappers.utils import connection

class GetLinkPipeline():

    @staticmethod
    def _get_asin(url):
        return url[url.find('dp/') + 3:url.find('?')]

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
                    category_id int unsigned not null,
                    url VARCHAR(100) UNIQUE,
                    asin VARCHAR(15),
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,
                    PRIMARY KEY(link_id)
                    );
            """
        )

    def process_item(self, item, spider):
        self.conn, self.curr = connection.connect()
        self._create_table()
        # if was error
        if isinstance(item, ErrorItem):
            self.curr.execute(
                """
                INSERT INTO errors(url, text, category)
                VALUES (%s, %s, %s)
                """,
                (
                    item['url'],
                    item['error_text'],
                    item['category']
            ))
        else:
            asin = self._get_asin(item['url'])
            self.curr.execute(
                """
                INSERT IGNORE INTO links(url, category, asin)
                VALUES (%s, %s, %s)
                """,
                (
                    item['url'],
                    item['category'],
                    asin
            ))
        self.conn.commit()
        return item


class GetCategoryPipeline():

    def _create_table(self):
        # error table
        self.curr.execute(
            """
                CREATE TABLE IF NOT EXISTS categories (
                    category_id int unsigned not null auto_increment,
                    name text,
                    url VARCHAR(200) UNIQUE,
                    status VARCHAR(10),
                    PRIMARY KEY(category_id)
                    );
            """
        )

    def process_item(self, item, spider):
        if item['name'] == 'Any Department':
            return item
        self.conn, self.curr = connection.connect()
        self._create_table()
        self.curr.execute(
            """
            INSERT IGNORE INTO categories(url, name, status)
            VALUES (%s, %s, %s)
            """,
            (
                item['url'],
                item['name'],
                item['status']
            ))
        self.conn.commit()
        return item