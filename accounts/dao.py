from datetime import date, timedelta
from django.db import connection, transaction

CAL_TABLE = "calendar_master"
NUM_TABLE = "numbering"
NG_COL = "ng_date"
RES_COL = "reservation_id"

class CalendarMaster:
    """施設不可日登録情報を操作するクラス"""

    @staticmethod
    def get_ngdate() -> list:
        """施設利用不可日を取得する"""
        today = date.today().strftime("%Y-%m-%d")
        with connection.cursor() as cursor:
            cursor.execute("select {ng_column} from {table} where ng_date >= '{today}'".format(ng_column=NG_COL, table=CAL_TABLE, today=today))
            result = cursor.fetchall()
            return [x[0] for x in result]

    @staticmethod
    def get_ngdata_in_month(year: int, month: int) -> list:
        """引数で受け取った月度の施設利用不可日を取得する"""
        today = date.today().strftime("%Y-%m-%d")
        with connection.cursor() as cursor:
            cursor.execute("select {ng_column} from {table} where (DATE_FORMAT({ng_column}, '%Y%m') = '{Y}{m}')".format(ng_column=NG_COL, table=CAL_TABLE, Y=str(year), m=str(month).zfill(2)))
            result = cursor.fetchall()
            return [x[0] for x in result]


    @staticmethod
    def set_ngdate(ng_date: date, reason:str):
        """施設利用不可日を設定する"""
        with connection.cursor() as cursor:
            cursor.execute("insert into {table} values('{ng_date}', '{reason}')".format(table=CAL_TABLE, ng_date=ng_date.strftime("%Y-%m-%d"), reason=reason))
            transaction.commit()

    @staticmethod
    def is_in_ngdate(start_date: date, end_date: date):
        """施設利用不可日に一致するか確認する"""
        ng_days = CalendarMaster.get_ngdate()
        for day in range((end_date - start_date).days):
            if start_date + timedelta(days=day) in ng_days:
                return True
        return False

class NumberingManagement:
    """採番テーブル"""

    @staticmethod
    def get_num():
        """採番テーブルの予約IDを更新（＋1）し、最新値を取得する"""
        with connection.cursor() as cursor:
            cursor.execute("update {table} t1 inner join (select {column} from {table} for update)t2 set t1.{column} = t2.{column} + 1".format(table=NUM_TABLE, column=RES_COL))

    @staticmethod
    def _get_num():
        """採番テーブルから予約IDを取得する"""
        with connection.cursor() as cursor:
            cursor.execute("select reservation_id from numbering")
            cursor.execute("update {table} t1 inner join (select {column} from {table} for update)t2 set t1.{column} = t2.{column} + 1 where current of current".format(table=NUM_TABLE, column=RES_COL))
            return cursor.fetchone()






