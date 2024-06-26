import logging
from data import DB_PORT, DB_USER, DB_NAME, DB_HOST, DB_PASSWORD
from psycopg2 import pool

# DB POSTGRESQL
class DB:
    connection_pool = pool.SimpleConnectionPool(minconn=1,
                                                maxconn=20,
                                                host=DB_HOST,
                                                dbname=DB_NAME,
                                                user=DB_USER,
                                                password=DB_PASSWORD,
                                                port=DB_PORT)
    
    conn = connection_pool.getconn()
    cursor = conn.cursor()

    def close_db(self):
        self.cursor.close()
        self.connection_pool.putconn(conn=self.conn)

    def save_user_id(self, user_id):
        self.cursor.execute("""INSERT INTO users (user_id, check_req, is_req_discount) VALUES ({}, 'n', FALSE)""".format(user_id))
        self.conn.commit()

    def update_save_user(self, user_id, name, phone_number, date_saved):
        sql = "UPDATE users SET name='{}', phone_number='{}', date_saved='{}', check_req='y'" \
              "WHERE user_id = {}"
        self.cursor.execute(sql.format(name, phone_number, date_saved, user_id))
        self.conn.commit()

    def get_user(self, user_id):
        sql = "SELECT * FROM users WHERE user_id = {};"
        self.cursor.execute(sql.format(user_id))
        user = self.cursor.fetchone()
        if user is not None:
            return (f'🆔: {user[0]}\n'
                    f'<b>Имя</b>: {user[2]}\n'
                    f'📞: {user[3]}\n'
                    f'🕘: {user[4]}\n'
                    f'<b><u>LINK</u></b>: <a href="tg://user?id={user_id}">Ссылка {user[2]}</a>\n')

    def check_request_user(self, user_id):
        sql = "SELECT user_id, check_req FROM users WHERE user_id = {} AND check_req = 'y';"
        self.cursor.execute(sql.format(user_id))
        result = self.cursor.fetchone()

        return result

    def get_users_id(self):
        self.cursor.execute("""SELECT user_id FROM users;""")
        users = self.cursor.fetchall()

        return [user[0] for user in users]

    def get_users_paginate(self, page_number):
        sql = 'SELECT id, user_id, name, phone_number, date_saved FROM users ORDER BY id DESC LIMIT {} OFFSET {}*{};'
        self.cursor.execute(sql.format(10, page_number - 1, 10))

        users = self.cursor.fetchall()

        return '\n'.join([f'🆔: {id}\n'
                          f'<b>Имя</b>: {name}\n'
                          f'📞: {phone_number}\n'
                          f'🕘: {date}\n'
                          f'<b><u>LINK</u></b>: <a href="tg://user?id={user_id}">Ссылка {name}</a>\n'
                          for id, user_id, name, phone_number, date in users])

    def get_count_users(self):
        self.cursor.execute("""SELECT COUNT(*) FROM users""")
        users = self.cursor.fetchone()
        return users[0]

    def get_user_id(self, id):
        self.cursor.execute("""SELECT * FROM users WHERE id = {};""".format(id))
        user = self.cursor.fetchone()
        if user is not None:
            return (f'🆔: {user[0]}\n'
                    f'<b>Имя</b>: {user[2]}\n'
                    f'📞: {user[3]}\n'
                    f'<b><u>LINK</u></b>: <a href="tg://user?id={user[1]}">Ссылка {user[2]}</a>\n')

    def delete_user(self, id):
        self.cursor.execute("""DELETE FROM users WHERE id = {};""".format(id))
        self.conn.commit()

    def update_res_discount(self):
        self.cursor.execute('UPDATE users SET is_req_discount = FALSE;')
        self.conn.commit()

    def update_req_discount(self, user_id):
        self.cursor.execute('UPDATE users SET is_req_discount = TRUE WHERE user_id = {}'.format(user_id))
        self.conn.commit()

    def is_req_discount(self, user_id):
        self.cursor.execute('SELECT is_req_discount FROM users WHERE user_id = {}'.format(user_id))
        response = self.cursor.fetchone()
        return response[0]


class DataBaseConnect:
    connection_pool = pool.SimpleConnectionPool(minconn=1,
                                                maxconn=20,
                                                host=DB_HOST,
                                                dbname=DB_NAME,
                                                user=DB_USER,
                                                password=DB_PASSWORD,
                                                port=DB_PORT)
    
    conn = connection_pool.getconn()
    cursor = conn.cursor()

    def create_db(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                               id SERIAL PRIMARY KEY,
                               user_id BIGINT UNIQUE,
                               name VARCHAR(40) NULL,
                               phone_number VARCHAR(13) NULL,
                               check_req VARCHAR(1) NULL,
                               is_req_discount BOOLEAN NULL,
                               date_saved VARCHAR(20) NULL);""")
        logging.info('create/connect DataBase')
        self.conn.commit()

        self.cursor.close()
        self.connection_pool.putconn(conn=self.conn)