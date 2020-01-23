import mysql.connector


def connect():
    conn = mysql.connector.connect(
        host='localhost',
        user='amazon_links',
        passwd='utor93lol',
        database='amazon_links'
    )
    curr = conn.cursor()
    return conn, curr
