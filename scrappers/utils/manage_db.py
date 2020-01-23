import mysql.connector


class ManageDB(object):

    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='amazon_links',
            passwd='utor93lol',
            database='amazon_links'
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
                    category text,
                    PRIMARY KEY(error_id)
                    );
            """
        )

    def insert_category(self, category):
        self.curr.execute(
            """
            INSERT IGNORE INTO categories(url, name, status)
            VALUES (%s, %s, %s)
            """,
            (
                category['url'],
                category['name'],
                category['status']
            ))
        self.conn.commit()

    def insert_error(self, error):
        self.curr.execute(
            """
            INSERT INTO errors(url, text, category)
            VALUES (%s, %s, %s)
            """,
            (
                error['url'],
                error['error_text'],
                error['category']
            ))
        self.conn.commit()

    def insert_link(self, link):
        self.curr.execute(
            """
            INSERT IGNORE INTO links(url, category, asin)
            VALUES (%s, %s, %s)
            """,
            (
                link['url'],
                link['category'],
                link['asin']
            ))
        self.conn.commit()

    def get_n_links(self, n):
        self.curr.execute(
            """
                SELECT * FROM categories
                WHERE status='new'
                LIMIT %s
            """,
            (
                n
            )
        )
        result = self.conn.fetchall()
        print(result)
