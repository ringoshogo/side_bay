from django.template.response import TemplateResponse
from accounts.models import User, UserDao, Reservations, ResDao, Lodging, LodginDao, Lottery_pool, LotDao
from accounts.util import test_send_email, send_password
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.sessions.models import Session
from dateutil.relativedelta import relativedelta
from accounts.dao import CalendarMaster
from operator import attrgetter

from .util import login_user

LOG_USR = "login_user_id"
ADMIN_USR = "adming_id"
LOG_NAME = "login_username"
LOG_MAIL = "login_mail_address"
KARA = ""

"""画面のURL"""
URL_REBGST001 = 'app/registration/REBGST_001.html'
MAIN_SCREEN = "app/registration/main.html"
URL_REBGST002 = "app/registration/REBGST_002.html"
URL_REBGST003 = "app/registration/REBGST_003.html"
URL_REBGST004 = "app/registration/REBGST_004.html"
URL_REBGST005 = "app/registration/REBGST_005.html"
URL_REBGST006 = "app/registration/REBGST_006.html"
URL_REBGST007 = "app/registration/REBGST_007.html"
URL_REBADM001 = "app/registration/REBADM_001.html"
URL_REBADM002 = "app/registration/REBADM_002.html"
URL_REBADM004 = "app/registration/REBADM_004.html"
URL_REBADM005 = "app/registration/REBADM_005.html"
TEST_SCREEN = "app/registration/test_database.html"
TEST_RES_SCREEN="app/registration/test_reservation.html"

"""抽選フラグ"""
ERROR = 0
LOTTERY = 1
SECOND_APP = 2

def init_login_screen(request):
    """ログイン処理を実施"""
    return TemplateResponse(request, URL_REBGST001, {})


def push_login_button(request):
    """初期処理、ログイン画面からログイン処理を実施。
    ・ID、パスワードが登録情報と一致しない場合、エラーメッセージをログイン画面に表示
    ・ID、パスワードが登録情報と一致する場合、予約画面へ遷移
    """

    # 画面からログイン認証情報(メールアドレス、パスワード)が送られてきた場合
    if request.method == 'POST':

        user_id = request.POST.get("user_id", "")
        password = request.POST.get("password","")
        user = UserDao.get_user(user_id)

        """エラーへの対処法 → no such table: django_session
        以下のコマンドを実施して、セッションテーブルを作成する
        python manage.py migrate --run-syncdb
        """
        # ユーザが存在する場合、セッション情報にユーザ情報を登録して、予約画面へ遷移
        if user is not None:
            if UserDao.check_password_between_user_and_input(user, password):

                #TODO 追って修正：ハードコーディング⇒DB取得
                #if user_id == 0:
                if True:
                    request.session[ADMIN_USR] = user.user_id
                    request.session[LOG_USR] = user.user_id
                    request.session[LOG_NAME] = user.username
                    request.session[LOG_MAIL] = user.mail_address
                else:
                    request.session[LOG_USR] = user.user_id
                    request.session[LOG_NAME] = user.username
                    request.session[LOG_MAIL] = user.mail_address


                return TemplateResponse(request, URL_REBGST002)
            # ユーザID、パスワードが登録情報と一致しない場合、ログイン画面を表示
            else:
                return TemplateResponse(request, URL_REBGST001,
                                        {"error": "Your password was not available!!",
                                         "user_id": user_id,})
        # ユーザが存在しない場合、ログイン画面を表示
        else:
            return TemplateResponse(request, URL_REBGST001,
                                    {"error": "Your username was not available!!",
                                     "user_id": user_id})
    # 初期処理の場合、ログイン画面を表示
    else:
        return TemplateResponse(request, URL_REBGST001, {})

def reset_password(request):
    """パスワードリセット"""

    # ユーザID、メールアドレスを取得
    user_id = request.POST.get("user_id", "")
    mail_address = request.POST.get("mail_address", "")

    # ユーザ情報をDBから取得
    target_user = UserDao.get_user(user_id)

    # ユーザ情報のメールアドレスと画面から取得したメールアドレスが一致するかチェック
    if UserDao.check_user_by_mail_address(target_user, mail_address):
        #TODO 汎用テーブルからパスワード初期値を取得
        password = "1234"

        #DBのユーザパスワードを初期値に更新
        UserDao.update_user_password(target_user, password)

        #TODO 登録のメールアドレスにパスワード初期化の旨を送信
        print("仮：メールアドレスにパスワード初期値を送信")

        return TemplateResponse(request, URL_REBGST001, {"error": ""})

    return TemplateResponse(request, URL_REBGST001,
                                {"error": "メールアドレスが登録されたメールアドレスと一致しません"})


def init_res_top_screen(request):
    """予約日入力画面の初期処理"""

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_login_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "セッションが切断されました"})

    return TemplateResponse(request, URL_REBGST002, {})


def __is_login_user(request) -> bool:
    """セッション情報にログインユーザ情報が存在するかを確認"""
    return LOG_USR in request.session


def __is_admini_user(request) -> bool:
    """セッション情報にユーザーIDが存在するかを確認"""
    return ADMIN_USR in request.session


def init_my_page_screen(request):
    """ログイン画面からログイン処理を実施。"""

    if not __is_login_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "セッションが切断されました"})

    login_user_res_info = []

    user_id = request.session[LOG_USR]
    if user_id:
        # ユーザの全ての予約・抽選を取得
        login_user_res_info.extend(ResDao.get_loginuserres_dto_by_user_id(user_id))
        login_user_res_info.extend(LotDao.get_loginuserres_dto_by_user_id(user_id))

        # 本日以降チェックアウト予定の予約・抽選のみ出力
        today = datetime.date.today()
        login_user_res_info = filter(lambda i: i.check_out_date >= today, login_user_res_info)

        # チェックイン日で降順に出力
        login_user_res_info = sorted(login_user_res_info, key=attrgetter('check_in_date'), reverse=True)

    return TemplateResponse(request, URL_REBGST003, {"login_user_res_info": login_user_res_info})

def push_res_app_button(request):
    """予約を実施

    """
    user_id = request.session[LOG_USR]

    from django.http import QueryDict
    dic = QueryDict(request.body, encoding='utf-8')
    check_in_date = datetime.date.fromisoformat(dic.get('check_in_date'))
    check_out_date = datetime.date.fromisoformat(dic.get('check_out_date'))
    number_of_rooms = dic.get('number_of_rooms')
    purpose = dic.get('purpose')

    error = ""

    #注意：現時点では宿泊人数を使用しないため、常に0を入力
    number_of_guests = 0

    # 抽選期間か2次申込期間かを取得
    app_status_code = __get_app_status_code(check_in_date)

    # 予約月度が過去月度の場合、エラー情報を画面に返却
    if app_status_code == ERROR:
        error = "予約申込対象期間外です"

    # 抽選の場合
    if app_status_code == LOTTERY:
        LotDao.create_res_by_in_and_out(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests,
                                        purpose)

    # 二次申込の場合
    if app_status_code == SECOND_APP:
        if not ResDao.create_res_as_second_reservation(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests, purpose):
            error = "二次申込が出来ませんでした"

    from django.http.response import JsonResponse
    return JsonResponse(error, safe=False)


def __get_app_status_code(check_in_date:datetime.date) -> int:
    """抽選か二次申込かを判定"""

    result = 0

    # 本申込締切日
    DEAD_LINE = 10

    # 当月度
    today = datetime.date.today()
    app_dead_line = today.replace(day=DEAD_LINE)

    # 抽選月度の初日と末日
    lottery_start_line = today.replace(day=1) + relativedelta(months=2)
    lottery_dead_line = today.replace(day=1) + relativedelta(months=3, days=-1)

    # 二次申込用の日付（翌月度の初日と最終日）
    next_month_first_day = lottery_start_line + relativedelta(months=-1)
    second_app_dead_line = lottery_start_line + relativedelta(days=-1)

    # 抽選期間の申込の場合
    if lottery_start_line < check_in_date and lottery_dead_line > check_in_date:
        result = LOTTERY
    # 翌月の場合
    if today < check_in_date and second_app_dead_line > check_in_date:
        if today < app_dead_line and check_in_date > next_month_first_day:
            pass
        else:
            result = SECOND_APP

    return result

def cancel_res_app(request):
    """抽選申込をキャンセル"""
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        LotDao.delete_by_reservation_id(reservation_id)
        LodginDao.delete_by_reservation_id(reservation_id)

    return init_my_page_screen(request)

def confirm_res(request):
    """予約の確定（本申込期間）"""
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        ResDao.change_request_status_to_confirm(reservation_id)

    return init_my_page_screen(request)

def cancel_res(request):
    """予約の確定（本申込期間）"""
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        ResDao.change_request_status_to_cancel(reservation_id)

    return init_my_page_screen(request)

def confirm_res_app(request):
    """テスト用予約の確定（本申込期間）"""
    #TODO delete this method
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        ResDao.create_res_by_lottery(reservation_id)
        LotDao.delete_by_reservation_id(reservation_id)
        return HttpResponseRedirect(reverse('test_reservation', {"error": ""} ))

    return TemplateResponse(request, URL_REBGST003)

def init_password(request):
    """画面側で入力したメールアドレスにパスワードを送信"""

    mail_address = request.POST.get("mail_address", "")

    if not mail_address == KARA:
        user = UserDao.get_user(mail_address)
        if user is not None:
            send_password(mail_address, user.password)


def logout_user(request):
    Session.objects.all().delete()
    print("session情報を表示")
    for session_info in UserDao.test_session():
        print(session_info.get_decoded())
    return TemplateResponse(request, URL_REBGST001, {})

def test_database(request):
    """
    テスト用のユーザー情報へ遷移する　
    :param request: request
    :return: ユーザー一覧画面
    """

    # POSTで情報が送られてきた場合、ユーザー情報を登録する
    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        username = request.POST.get("username", "")
        mail_address = request.POST.get("mail_address", "")
        password = request.POST.get("password", "")
        UserDao.create_user(user_id, username, mail_address, password)

    # 一覧表示するユーザー情報を取得
    users = UserDao.get_users()

    return TemplateResponse(request, TEST_SCREEN, {"users": users, "json_data": None})

def test_get_back_database(request, user_id):
    """予約画面からユーザー一覧画面へ戻る"""
    return HttpResponseRedirect(reverse('test_database'))

def test_reservation(request, user_id):
    """
    テスト用の予約作成画面へ遷移する
    :param request: request
    :param mail_address: 宿泊対象者のメールアドレス
    :return: 対象ユーザーの宿泊予約一覧画面
    """

    # 対象のユーザーネームを取得
    user = UserDao.get_user(user_id)

    # 対象のユーザーアドレスに紐づく宿泊日付を取得
    reservations = ResDao.get_res_list(user_id)
    lotterys = LotDao.get_res_list(user_id)

    return TemplateResponse(request, TEST_RES_SCREEN, {"reservations": reservations,"lotterys": lotterys, "username": user.username})


def register_reservation(request, user_id):
    """
    予約情報を登録する
    :param request: request
    :param mail_address: 宿泊登録者のメールアドレス
    :return: ユーザー一覧画面
    """

    if request.method == "POST":
        lottery_flag = request.POST.get("lottery_flag", None)
        check_in_date = datetime.date.fromisoformat(request.POST.get("check_in_date", ""))
        check_out_date = datetime.date.fromisoformat(request.POST.get("check_out_date", ""))
        number_of_rooms = request.POST.get("number_of_rooms", "")
        number_of_guests = request.POST.get("number_of_guests", "")
        purpose = request.POST.get("purpose", "")

        # 抽選フラグが"1"の場合、抽選エンティティを作成
        if lottery_flag:
            LotDao.create_res_by_in_and_out(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests,
                                            purpose)

        # 抽選フラグが指定されていない場合、予約エンティティを作成
        else:
            ResDao.create_res_by_in_and_out(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests, purpose)

    # 表示するユーザー情報を取得
    users = UserDao.get_users()

    return HttpResponseRedirect(reverse('test_reservation', args=(user_id,)))

def turn_lottery_into_reservation(request, user_id):
    """TODO 削除予定
    抽選エンティティを予約エンティティへ変換する
    :param request:
    :param user_id:
    :param reservation_id:
    :return:
    """
    reservation_id = int(request.POST.get("reservation_id", 0))
    print("reservation_idは",reservation_id)
    ResDao.create_res_by_lottery(reservation_id)
    LotDao.delete_by_reservation_id(reservation_id)
    return HttpResponseRedirect(reverse('test_reservation', args=(user_id,)))

def delete_lottery_or_reservation(request, user_id):
    """
    予約IDに紐づく予約or抽選情報を削除する
    :param request:
    :param user_id:
    :return:
    """
    reservation_id = int(request.POST.get("reservation_id", 0))
    if reservation_id:
        ResDao.delete_by_reservation_id(reservation_id)
        LotDao.delete_by_reservation_id(reservation_id)
        LodginDao.delete_by_reservation_id(reservation_id)

    return HttpResponseRedirect(reverse('test_reservation', args=(user_id,)))

def test_delete_user(request):
    """
    ユーザIDに紐づくユーザーを削除する
    :param user_id: ユーザID
    :return:
    """
    user_id = int(request.POST.get("user_id", 0))
    if user_id:
        UserDao.delete_user_by_user_id(user_id)
        ResDao.delete_by_user_id(user_id)
        LotDao.delete_by_user_id(user_id)
        LodginDao.delete_by_user_id(user_id)

    return HttpResponseRedirect(reverse('test_database'))


def get_back_to_main_from_test_register(request, user_id):
    """
    ユーザー登録画面からログイン画面へ遷移する
    :param request: request
    :param user_id: 宿泊者のユーザID
    :return: ユーザー一覧画面
    """

    # 表示するユーザー情報を取得
    users = UserDao.get_users()

    return TemplateResponse(request, URL_REBGST001, {})


#TODO 未着手
def init_password_change(request):
    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_login_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "セッションが切断されました"})

    return TemplateResponse(request, URL_REBGST005, {})


def change_password(request):
    """パスワードを変更する"""

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_login_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "セッションが切断されました"})

    # 現パスワード、新パスワード、新パスワード確認版を取得する
    old_password = request.POST.get("old_password", "")
    new_password = request.POST.get("new_password", "")
    new_password_conf = request.POST.get("new_password_conf", "")

    # ログインユーザ情報を取得する
    user = UserDao.get_user(request.session[LOG_USR])

    # 現パスワードがユーザーの登録パスワードと一致するか確認する
    if not UserDao.check_password_between_user_and_input(user, old_password):
        return TemplateResponse(request, URL_REBGST005, {"error": "現在のパスワードが正しくありません。"})

    # 新パスワードと新パスワード確認用が一致するか確認する
    if new_password != new_password_conf:
        return TemplateResponse(request, URL_REBGST005, {"error": "新しいパスワードと確認用パスワードが一致しません。"})

    # 新パスワードを更新する
    UserDao.update_user(user.user_id, user.username, user.mail_address, new_password)
    return TemplateResponse(request, URL_REBGST005, {"error":"", "success": "パスワード変更に表示しました"})


def init_admin_manage(request):
    """（管理者専用）管理者画面の初期表示"""

    # セッション情報に管理者IDが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_admini_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "管理者権限がありません"})

    # 全ユーザ情報を取得
    users = UserDao.get_users()

    return TemplateResponse(request, URL_REBADM001, {"users": users})


def register_new_user(request):
    """（管理者専用）新規ユーザを登録する"""

    # セッション情報に管理者IDが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_admini_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "管理者権限がありません"})

    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        username = request.POST.get("user_name", "")
        mail_address = request.POST.get("mail_address", "")
        #TODO 初期パスワードを汎用マスタから取得する処理に修正する
        password = "rebirth123"
        UserDao.create_user(user_id, username, mail_address, password)

        # 全ユーザ情報を取得
        users = UserDao.get_users()

    return TemplateResponse(request, URL_REBADM001, {"users": users})

def update_user(request):
    """（管理者専用）ユーザ情報を更新する"""

    # セッション情報に管理者IDが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_admini_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "管理者権限がありません"})

    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        username = request.POST.get("user_name", "")
        mail_address = request.POST.get("mail_address", "")
        UserDao.update_user_without_password(user_id, username, mail_address)

        # 全ユーザ情報を取得
        users = UserDao.get_users()

    return TemplateResponse(request, URL_REBADM001, {"users": users})

def delete_user(request):
    """（管理者専用）ユーザ情報を更新する"""

    # セッション情報に管理者IDが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_admini_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "管理者権限がありません"})

    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        if user_id:
            UserDao.delete_user_by_user_id(user_id)
            ResDao.delete_by_user_id(user_id)
            LotDao.delete_by_user_id(user_id)
            LodginDao.delete_by_user_id(user_id)

        # 全ユーザ情報を取得
        users = UserDao.get_users()

    return TemplateResponse(request, URL_REBADM001, {"users": users})

#TODO 未着手
def init_admin_calendar(request):
    """（管理者専用）管理者専用カレンダーの初期表示"""

    # セッション情報に管理者IDが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_admini_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "管理者権限がありません"})

    return TemplateResponse(request, URL_REBADM002, {})


def prohibit_res(request):
    """（管理者専用）施設利用不可日を登録"""
    error = ""
    # セッション情報に管理者IDが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_admini_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "管理者権限がありません"})

    from django.http import QueryDict
    dic = QueryDict(request.body, encoding='utf-8')
    ng_date = dic.get('ng_date')
    reason = dic.get('reason')
    CalendarMaster.set_ngdate(datetime.date.fromisoformat(ng_date), reason)

    from django.http.response import JsonResponse
    return JsonResponse(error, safe=False)


def init_user_terms(request):

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_login_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "セッションが切断されました"})

    return TemplateResponse(request, URL_REBGST006, {})


def init_sidebay_info(request):

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    if not __is_login_user(request):
        return TemplateResponse(request, URL_REBGST001, {"error": "セッションが切断されました"})

    return TemplateResponse(request, URL_REBGST007, {})
