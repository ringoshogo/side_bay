from django.urls import path
from . import views, util








urlpatterns = [

    # ログイン画面
    path('', views.init_login_screen, name='top'),
    path(r'push_login_button', views.push_login_button, name='main'),
    path(r'reset_password', views.reset_password, name='reset_password'),

    # 予約トップ画面
    path(r'init_res_top_screen', views.init_res_top_screen, name='init_res_top_screen'),

    # マイページ画面
    path(r'init_my_page_screen', views.init_my_page_screen, name='init_my_page_screen'),
    path(r'cancel_res_app', views.cancel_res_app, name='cancel_res_app'),
    path(r'confirm_res', views.confirm_res, name='confirm_res'),
    path(r'cancel_res', views.cancel_res, name='cancel_res'),

    # 予約入力画面
    path(r'push_res_app_button', views.push_res_app_button, name='push_res_app_button'),

    # パスワード変更画面
    path(r'init_password_change', views.init_password_change, name='init_password_change'),
    path(r'change_password', views.change_password, name='change_password'),

    # ユーザ一覧
    path(r'init_admin_manage', views.init_admin_manage, name='init_admin_manage'),

    # 管理者カレンダー
    path(r'init_admin_calendar', views.init_admin_calendar, name='init_admin_calendar'),

    # 利用規約
    path(r'init_user_terms', views.init_user_terms, name='init_user_terms'),
    path(r'prohibit_res', views.prohibit_res, name='prohibit_res'),

    # ユーザ管理
    path(r'init_sidebay_info', views.init_sidebay_info, name='init_sidebay_info'),

    # JSON操作
    path(r'get_all_res_info', util.get_all_res_info, name='create_json_info'),
    path(r'get_login_user_res_info', util.get_login_user_res_info, name='get_login_user_res_info'),

    # path(r'login', views.login, name='login'),
    path(r'logout', views.logout_user, name='logout'),

    # 予約情報管理用URL
    path(r'test_reservation/<str:user_id>/', views.test_reservation, name="test_reservation"),
    path(r'test_reservation/<str:user_id>/test_database', views.test_get_back_database, name="test_get_back_database"),
    path(r'test_reservation/<str:user_id>/register_reservation', views.register_reservation, name="register_reservation"),
    path(r'test_reservation/<str:user_id>/turn_lottery_into_reservation', views.turn_lottery_into_reservation, name="turn_lottery_into_reservation"),
    path(r'test_reservation/<str:user_id>/delete_lottery_or_reservation', views.delete_lottery_or_reservation, name="delete_lottery_or_reservation"),

    # ユーザ情報管理用URL
    path(r'test_database', views.test_database, name="test_database"),
    path(r'test_delete_user', views.test_delete_user, name="test_delete_user"),

    path(r'register_new_user', views.register_new_user, name="register_new_user"),
    path(r'update_user', views.update_user, name="update_user"),
    path(r'delete_user', views.delete_user, name="delete_user"),


    # テストデータ作成用
    path(r'confirm_res_app', views.confirm_res_app, name='confirm_res_app'),
]
