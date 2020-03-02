import unittest
import mysql.connector

import manage_db

MANAGE = manage_db.ManageDB()


def get_from_table(table_name, field_name, field_val):
    query = """
        SELECT * FROM {} 
        WHERE {}="{}"
    """.format(table_name, field_name, field_val)

    MANAGE.curr.execute(query)

    return MANAGE.curr.fetchall()


def delete_from_table(table_name, field_name, field_val):
    query = """
        DELETE FROM {} WHERE {}="{}"
    """.format(table_name, field_name, field_val)

    MANAGE.curr.execute(query)

    MANAGE.conn.commit()


def create_test_category(depth):
    url = 'http://test_cat.com' + str(depth)
    query = """
        INSERT IGNORE INTO categories(url, name, status, depth)
        VALUES ("{}", "{}", "{}", {})
    """.format(url, 'test_cat_' + str(depth), 'new', depth)
    MANAGE.curr.execute(query)
    MANAGE.conn.commit()

    query = """
        SELECT category_id
        FROM categories
        WHERE url="{}"
    """.format(url)
    MANAGE.curr.execute(query)
    res = MANAGE.curr.fetchall()
    return res[0]['category_id']


def insert_test_decorator(func):
    def wrapper(self):
        func(self)
        res = get_from_table(self.table_name, self.field_name, self.field_value)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][self.field_name], self.field_value)
        return True
    return wrapper


class InsertCategoryTest(unittest.TestCase):

    def setUp(self) -> None:
        self.table_name = 'categories'
        self.field_name = 'url'
        self.field_value = 'http://test_case.com'

        self.d = {
                    self.field_name: self.field_value,
                    'name': 'Test case',
                    'status': 'new',
                    'depth': 1
                  }

    @insert_test_decorator
    def test_good(self):
        MANAGE.insert_category(self.d)

    @insert_test_decorator
    def test_duplicate(self):
        MANAGE.insert_category(self.d)
        MANAGE.insert_category(self.d)

    def tearDown(self) -> None:
        delete_from_table(self.table_name, self.field_name, self.field_value)


class InsertErrorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.table_name = 'errors'
        self.field_name = 'url'
        self.field_value = 'http://test_case.com'

        self.d = {
                self.field_name: self.field_value,
                'error_text': 'Test case',
                'category_id': 1,
        }

    @insert_test_decorator
    def test_good(self):
        MANAGE.insert_error(self.d)

    def tearDown(self) -> None:
        delete_from_table(self.table_name, self.field_name, self.field_value)


class InsertLinkTest(unittest.TestCase):

    def setUp(self) -> None:
        self.table_name = 'links'
        self.field_name = 'url'
        self.field_value = 'http://test_case.com'

        self.category_id = create_test_category(10)
        self.d = {
            self.field_name: self.field_value,
            'asin': 'test_asin',
            'category_id': self.category_id
        }

    @insert_test_decorator
    def test_good(self):
        MANAGE.insert_link(self.d)

    @insert_test_decorator
    def test_duplicate(self):
        MANAGE.insert_link(self.d)
        MANAGE.insert_link(self.d)

    def test_bigger_depth(self):
        """
        Create link
        Create new category with bigger depth
        Create new link with new category
        Get created link from table
        Get category which relation with taken link
        Test
        """
        MANAGE.insert_link(self.d)

        new_category_id = create_test_category(11)
        new_d = {
            self.field_name: self.field_value,
            'asin': 'test_asin',
            'category_id': new_category_id
        }
        MANAGE.insert_link(new_d)

        res = get_from_table(self.table_name, self.field_name, self.field_value)
        category_id = res[0]['category_id']

        res = get_from_table('categories', 'category_id', category_id)
        self.assertEqual(res[0]['depth'], 11)
        delete_from_table('categories', 'category_id', category_id)

    def tearDown(self) -> None:
        delete_from_table(self.table_name, self.field_name, self.field_value)
        delete_from_table('categories', 'category_id', self.category_id)


if __name__ == '__main__':
    unittest.main()

