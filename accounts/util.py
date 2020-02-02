from django.contrib.auth import login
from django.core.mail import BadHeaderError, send_mail
from accounts.models import UserDao, ResDao, LodginDao, LotDao
from accounts.dao import CalendarMaster

# 固定値
LOG_USR = "login_user_id"
EMPTY_STR = ""

def login_user(request, user):
    login(request, user)

def res_send_mail(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)

def test_send_email():
    """題名"""
    subject = "題名"

    """本文"""
    message = "本文です/n林翔吾用のテストです"
    """送信元メールアドレス"""
    from_email = "information@res_system.com"
    """宛先メールアドレス"""
    recipient_list = [
        "sennseikou@gmail.com"
    ]
    res_send_mail(subject, message, from_email, recipient_list)

def send_password(mail_address: str, password: str):
    """
    引数のメールアドレスに引数のパスワードを送付する
    :param mail_address: メールアドレス
    :param password: メールアドレスに紐づくパスワード
    :return: なし
    """
    subject = "パスワード再送"
    message = "password: " + password
    from_email = "information@res_system.com"
    recipient_list = [
        mail_address
    ]
    res_send_mail(subject, message, from_email, recipient_list)

"""
JSONの返却処理を実施
"""

import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http.response import JsonResponse


@ensure_csrf_cookie
    # 取得した文字列の日付を日付型に変換
def get_all_res_info(request):

    # 日付を取得
    target_day_str = request.GET.get("yyyymm")

    target_day = datetime.date(int(target_day_str[0:4]), int(target_day_str[4:6]), 1) - relativedelta(months=1)

    # 結果を格納する変数
    data = []

    # 当月と前後1か月分のjsonデータを取得
    for i in range(3):# 0～2までの数列
        next_day = target_day + relativedelta(months=i)
        next_month = next_day.month
        next_year = next_day.year
        data.extend(JsonFactory.create_res_info_by_year_month(next_year, next_month))

    return JsonResponse(data, safe=False)


@ensure_csrf_cookie
def get_login_user_res_info(request):
    """ログインユーザの予約情報を取得"""

    # ログインユーザのユーザIDを取得
    user_id = request.session[LOG_USR]

    # ログインユーザから宿泊情報のJSONを取得
    data = JsonFactory.create_login_user_res_info_by_user_id(user_id)

    return JsonResponse(data, safe=False)


class JsonFactory:
    """
    ユーザー情報をjson形式に作成するクラス
    """

    # カレンダー情報
    IN_USE = "空室：×"
    VACANT = "空室：{num}部屋"
    BANNED = "施設利用不可"
    RES_DATE = "start"
    USER = "user"
    TITLE_ROOMS = "title"
    COLOR = "color"
    TEXT_COLOR = "textColor"

    # ログインユーザの抽選、予約情報
    RES_ID = "res_id"
    APP_STATUS = "app_status"
    IN_DATE = "check_in_date"
    OUT_DATE = "check_out_date"
    NUM_ROOMS = "number_of_rooms"
    EXPIRE = "expire_date"
    PRIORITY = "priority"

    @staticmethod
    def create_res_info_by_year_month(year: int, month: int) -> list:
        """
        カレンダー表示用のjsonデータを作成する
        :param month: 取得対象となるjsonデータ
        :return: list形式のjsonデータ
        """

        # key = 日付情報、value = タイトル、予約者、日付情報の辞書型を作成
        reservation_dict = {}

        # 該当月度の最終日
        _, lastday = calendar.monthrange(year, month)

        # 全ての日付に空の予約情報を設定
        for res_date_day in range(lastday): # 0,1,2,…,lastday - 1
            res_date = datetime.date(year,month,res_date_day + 1).strftime('%Y-%m-%d')
            reservation_dict[res_date] = {JsonFactory.RES_DATE: res_date, JsonFactory.TITLE_ROOMS: 0}

        # 指定の年月から予約情報を取得
        res_list = ResDao.get_res_by_year_and_month(year, month)

        # 予約情報のQuerySetを取得からjson情報を作成する
        for res_set in res_list:

            # 予約情報が持つ連泊数ごとにjsonレコードを作成・追記
            for lodging_date in LodginDao.get_lodging_by_reservation_id(res_set.reservation_id):

                # チェックイン日と連泊日数をもとに、キーとなる日付を取得
                res_date = lodging_date.lodging_date.strftime('%Y-%m-%d')

                json_data = reservation_dict.setdefault(res_date, {JsonFactory.RES_DATE:res_date, JsonFactory.TITLE_ROOMS: 0})
                checkin_user = JsonFactory.USER + str(len(json_data) - 1)
                json_data[checkin_user] = "{username}: {rooms}部屋".format(username=UserDao.get_user(res_set.user_id).username, rooms=res_set.number_of_rooms)
                json_data[JsonFactory.TITLE_ROOMS] = json_data[JsonFactory.TITLE_ROOMS] + res_set.number_of_rooms

        for res_inf in reservation_dict.values():
            room_count = res_inf[JsonFactory.TITLE_ROOMS]
            if room_count > 3:
                res_inf[JsonFactory.TITLE_ROOMS] = JsonFactory.IN_USE
                res_inf[JsonFactory.COLOR] = "black"
                res_inf[JsonFactory.TEXT_COLOR] = "white"
            else:
                res_inf[JsonFactory.TITLE_ROOMS] = JsonFactory.VACANT.format(num=(4 - room_count))


        # 施設利用不可日の登録
        for ng in CalendarMaster.get_ngdata_in_month(year, month):
            ng_date = ng.strftime('%Y-%m-%d')
            reservation_dict[ng_date] = {JsonFactory.RES_DATE: ng_date, JsonFactory.TITLE_ROOMS: JsonFactory.BANNED, JsonFactory.COLOR: "black", JsonFactory.TEXT_COLOR: "while"}


        # テスト用にreturnを実施
        return list(reservation_dict.values())

    @staticmethod
    def create_login_user_res_info_by_user_id(user_id: int) -> list:
        """ログインユーザに紐づく抽選、宿泊情報を取得"""



        # 返却結果
        result = []

        # 対象ユーザに紐づく抽選、予約情報を取得
        reservations = ResDao.get_res_list(user_id)
        lotterys = LotDao.get_res_list(user_id)

        # 抽選情報の辞書型を作成
        for lottery in lotterys:
            lottery_dict = {}
            lottery_dict[JsonFactory.RES_ID] = lottery.reservation_id
            lottery_dict[JsonFactory.APP_STATUS] = 0
            lottery_dict[JsonFactory.IN_DATE] = lottery.check_in_date
            lottery_dict[JsonFactory.OUT_DATE] = lottery.check_out_date
            lottery_dict[JsonFactory.NUM_ROOMS] = lottery.number_of_rooms
            lottery_dict[JsonFactory.EXPIRE] = EMPTY_STR
            lottery_dict[JsonFactory.PRIORITY] = lottery.priority
            result.append(lottery_dict)

        # 予約情報の辞書型を作成
        for reservation in reservations:
            reservation_dict = {}
            reservation_dict[JsonFactory.RES_ID] = reservation.reservation_id
            reservation_dict[JsonFactory.APP_STATUS] = reservation.request_status + 1
            reservation_dict[JsonFactory.IN_DATE] = reservation.check_in_date
            reservation_dict[JsonFactory.OUT_DATE] = reservation.check_out_date
            reservation_dict[JsonFactory.NUM_ROOMS] = reservation.number_of_rooms
            reservation_dict[JsonFactory.EXPIRE] = reservation.expire_date
            reservation_dict[JsonFactory.PRIORITY] = EMPTY_STR
            result.append(reservation_dict)

        return result

