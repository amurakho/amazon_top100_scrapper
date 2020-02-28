import mysql.connector

import conf


class ManageDB(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ManageDB, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.conn = mysql.connector.connect(
            host=conf.HOST,
            user=conf.USER,
            passwd=conf.PASSWD,
            database=conf.DATABASE
        )
        self.curr = self.conn.cursor()

        self._create_dbs()

    def _create_dbs(self):
        # create category db
        self.curr.execute(
            """
                CREATE TABLE IF NOT EXISTS categories (
                    category_id int unsigned not null auto_increment,
                    name text,
                    url VARCHAR(200) UNIQUE,
                    status VARCHAR(10),
                    depth int,
                    PRIMARY KEY(category_id)
                    );
            """
        )

        # create links db
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

        # create errors db
        self.curr.execute(
            """
                CREATE TABLE IF NOT EXISTS errors (
                    error_id int unsigned not null auto_increment,
                    text text,
                    url text,
                    category_id int unsigned not null,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,
                    PRIMARY KEY(error_id)
                    );
            """
        )

    def insert_category(self, category):
        query = """
            SELECT * 
            FROM categories
            WHERE url="{}"
            LIMIT 1
        """.format(category['url'])
        self.curr.execute(query)
        result = self.curr.fetchall()

        if result:
            return

        self.curr.execute(
            """
            INSERT IGNORE INTO categories(url, name, status, depth)
            VALUES (%s, %s, %s, %s)
            """,
            (
                category['url'],
                category['name'],
                category['status'],
                category['depth'],
            ))
        self.conn.commit()

    def insert_error(self, error):
        query = """
             INSERT IGNORE INTO errors(url, text, category_id)
             SELECT '{}', '{}', category_id
                 FROM categories
                 WHERE category_id={}
                 LIMIT 1
         """.format(error['url'], error['error_text'], error['category_id'])
        self.curr.execute(query)
        self.conn.commit()

    def insert_link(self, link):
        # query = """
        #         -- create first variable for old category(depth, id)
        #         SELECT @old_category_depth:=depth, @old_category_id:=categories.category_id
        #         FROM links
        #         JOIN categories ON categories.category_id=links.category_id
        #         WHERE links.url='{}' LIMIT  1;
        #         -- create second variable for new category(depth, id)
        #         SELECT @new_category_depth:=depth, @new_category_id:=categories.category_id
        #         FROM categories
        #         WHERE category_id=2 LIMIT  1;
        #         -- insert new link if it not duplicate
        #         INSERT INTO links(url, asin, category_id)
        #             SELECT '{}', '{}', category_id
        #             FROM categories
        #             WHERE category_id=2 LIMIT 1
        #         ON DUPLICATE KEY UPDATE category_id=
        #         -- if duplicate(you can see what it mean from variables name(i hope me from future didnt killmyself))
        #             CASE
        #                 WHEN (SELECT @old_category_depth)>(SELECT @new_category_depth)
        #                 THEN (SELECT @old_category_id)
        #                 ELSE (SELECT @new_category_id)
        #             END;
        # """.format(link['url'], link['url'], link['asin'], link['category_id'])
        query = """
            INSERT IGNORE INTO links(url, asin, category_id)
            VALUES  ("{}", "{}", {})
        """.format(
                link['url'],
                link['asin'],
                link['category_id']
              )
        self.curr.execute(query)
        self.conn.commit()

    def get_n_links(self, n, status):
        query = """
                SELECT * FROM categories
                WHERE status='{}'
                LIMIT {};
            """.format(status, 10)
        self.curr.execute(query)
        result = self.curr.fetchall()
        self.curr.nextset()
        self.conn.commit()
        return result

    def change_category_status(self, category_id, status):
        query = """
            UPDATE categories
            SET status='{}'
            WHERE category_id={};
        """.format(status, category_id)
        self.curr.execute(query)
        self.conn.commit()
