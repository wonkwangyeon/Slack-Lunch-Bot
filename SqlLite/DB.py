import sqlite3
from toollib.logger import Logger
from pathlib import Path


class DB(object):
    logger = Logger("DB")

    def __init__(self):
        if not Path('db/meal.db').is_file():
            self.conn = sqlite3.connect("db/meal.db")
            self.cur = self.conn.cursor()
            self.db_init_table()
        else:
            self.conn = sqlite3.connect("db/meal.db")
            self.cur = self.conn.cursor()

    def db_init_table(self):
        self.logger.info("SQLite3 초기화")
        self.conn.execute("""
                   CREATE TABLE IF NOT EXISTS menu (
                       name TEXT NOT NULL PRIMARY KEY  /* 메뉴 이름 */                     
                   )
               """)
        self.conn.commit()

        self.conn.execute("""
                           CREATE TABLE IF NOT EXISTS menu_log (
                               id integer primary key autoincrement,  /* 로그 고유번호 */
                               name text not null,                     /* 메뉴 이름 */
                               time timestamp DATE DEFAULT(datetime('now', 'localtime'))   /* 날짜 */                     
                           )
                       """)
        self.conn.commit()

    def select_all(self):
        try:
            sql = "SELECT name FROM menu"

            self.cur.execute(sql)
            rows = self.cur.fetchall()
            if (len(rows)) == 0:
                return None
            else:
                return rows

        except Exception as e:
            self.logger.debug(e)
            return "DB 에러발생."

    def insert_by_name(self, menu):
        try:
            sql = "insert into menu(name) values(?)"
            self.cur.execute(sql, (menu, ))
            self.conn.commit()
            return "추가하였습니다."

        except sqlite3.IntegrityError:
            self.logger.debug("메뉴 중복")
            return None

        except Exception as e:
            self.logger.debug(e)
            return True

    def delete_by_name(self, menu):
        try:
            sql = "delete from menu where name = ?"
            self.cur.execute(sql, (menu, ))
            self.conn.commit()
            return "삭제하였습니다."

        except Exception as e:
            self.logger.debug(e)
            return "DB 에러발생."

    def select_random(self):
        try:
            sql = "select name from menu order by random() limit 1"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            if row is None:
                return None
            else:
                (ret_value, ) = row
                return ret_value

        except Exception as e:
            self.logger.debug(e)
            return "DB 에러발생."

    def insert_log(self, menu_name):
        try:
            sql = "insert into menu_log(name) values(?)"
            self.cur.execute(sql, (menu_name,))
            self.conn.commit()
            self.logger.debug("로그 추가")

        except Exception as e:
            self.logger.debug(e)
            return "DB 에러발생."

    def find_log_by_date(self, date):
        try:
            sql = "select * from menu_log where date(time) = date(?) limit 1"
            self.cur.execute(sql, (date,))
            r1, r2, r3 = self.cur.fetchone()
            return str(r1) + " : " + r2 + " "+ r3

        except Exception as e:
            self.logger.debug(e)
            return "DB 에러발생."

    def __del__(self):
         self.conn.close()
