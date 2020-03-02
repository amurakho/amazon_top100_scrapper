import mysql.connector

from . import conf


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
        self.curr = self.conn.cursor(dictionary=True)

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

        query = """
            INSERT IGNORE INTO categories(url, name, status, depth)
            VALUES ("{}", "{}", "{}", {})
            """.format(
                category['url'],
                category['name'],
                category['status'],
                category['depth'],
            )
        self.curr.execute(query)
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
        # try to get info about already saved link
        query = """
                SELECT categories.depth, categories.category_id, links.link_id
                FROM links
                JOIN categories ON categories.category_id=links.category_id
                WHERE links.url="{}" LIMIT  1;
        """.format(link['url'])
        self.curr.execute(query)
        old_category = self.curr.fetchall()

        if old_category:
            # get depth of new category
            query = """
                    SELECT depth, categories.category_id
                    FROM categories
                    WHERE category_id={} LIMIT  1;
            """.format(link['category_id'])
            self.curr.execute(query)
            new_category = self.curr.fetchall()
            if new_category[0]['depth'] > old_category[0]['depth']:
                query = """
                    UPDATE links
                    SET 
                        category_id={}
                    WHERE
                        link_id={}
                """.format(new_category[0]['category_id'], old_category[0]['link_id'])
                self.curr.execute(query)
                self.conn.commit()

        else:
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
