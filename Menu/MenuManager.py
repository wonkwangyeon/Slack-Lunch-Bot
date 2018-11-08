from SqlLite.DB import DB
from random import *
import datetime
from toollib.logger import Logger


class MenuManager(object):
    logger = Logger("MenuManager")

    def __init__(self):
        self.db = DB()
        self.menu = []

    def menu_setting(self):
        self.menu.clear()
        rows = self.db.select_all()   # 메뉴 전체 가져오기
        if rows is None:
            return "데이터베이스에 추가된 메뉴 없음"

        for (row, ) in rows:            # 메뉴 추가
            self.menu.append(row)
        return "메뉴 세팅완료."

    def all_menu_check(self):   # 모든 메뉴 확인
        rows = self.db.select_all()

        if rows is None:
            return "데이터베이스에 추가된 메뉴 없음"

        all_menu = ""
        i = 0
        for (row, ) in rows:
            i += 1
            if i == len(rows):
                all_menu += row
            else:
                all_menu += row + " / "
        return all_menu

    def menu_rand_select(self):
        rand_num = randrange(len(self.menu))    # 번호 추출
        today_menu = self.menu[rand_num]    # 랜덤으로 메뉴 뽑기
        del self.menu[rand_num]     # 뽑은 메뉴를 삭제.
        self.db.insert_log(today_menu)  # 오늘 먹은 메뉴 기록.
        return today_menu

    def menu_insert(self, menu_name):
        result = self.db.insert_by_name(menu_name)
        if result is None:
            return "이미 추가되어있는 메뉴입니다."
        elif result is True:
            return "DB 에러"
        self.menu.append(menu_name)
        return result

    def menu_delete(self, menu_name):
        try:
            result = self.db.delete_by_name(menu_name)
            self.menu.remove(menu_name)
            return result

        except ValueError:
            return "존재하지 않는 메뉴입니다"

    def menu_recommend(self):
        result = self.db.select_random()
        if result is None:
            return "추가된 메뉴가 없음."
        return result

    def find_menu_log(self, date):
        result = self.db.find_log_by_date(date)
        if result is None:
            return date+"에 먹은 음식이 존재하지 않습니다."

        return result
