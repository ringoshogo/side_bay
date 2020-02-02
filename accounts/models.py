


from django.db import models
from django.db import transaction
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.models import Session
from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Max
from accounts.dto import LoginUserResInfo
from accounts.dao import CalendarMaster

import bcrypt

from django.db import connection

TOBEDETERMINED = 0
DETERMINED = 1
CANCEL = 2

# 試しにメールアドレスでのログイン機能を実装するためのコードを書いてみる
class UserManager(BaseUserManager):
    """ユーザーマネージャー"""

    user_in_migrations = True

    def _create_user(self, mail_address, password, **extra_fields):
        """メールアドレスの登録を必須にする"""
        if not mail_address:
            raise ValueError('The given email must be set')
        email = self.normalize_email(mail_address)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mail_address, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(mail_address, password, **extra_fields)

    def create_superuser(self, mail_address, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(mail_address, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    ユーザ情報を提供するDTOクラス
    """
    user_id = models.IntegerField(_('ユーザID'), primary_key=True)
    username = models.CharField(_('ユーザ名'), max_length=40, default=None, blank=True)
    mail_address = models.EmailField(_('メールアドレス'), unique=True, default=None)
    password = models.CharField(_('パスワード'), max_length=128, default=None) #パスワードの入力制限は設けるか

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    EMAIL_FIELD = 'mail_address'
    USERNAME_FIELD = 'mail_address'
    REQUIRED_FIELDS = []


class UserDao:
    """Userオブジェクトを操作するクラス"""

    @staticmethod
    def get_user(user_id: int) -> User:
        """Userオブジェクトを取得

        :param mail_address メールアドレス
        """
        try:
            return User.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            print("対象のオブジェクトがDBに存在しません")

    @staticmethod
    def check_user_by_mail_address(user: User, mail_address: str) -> bool:
        """引数のユーザが保持するメールアドレスと引数のメールアドレスが一致するかチェック"""
        return user.mail_address == mail_address

    @staticmethod
    def get_users():
        return User.objects.order_by('user_id')

    @staticmethod
    def create_user(user_id:int, username:str, mail_address:str, password:str):
        """"""
        #TODO メールアドレスの2重登録にならないような処理を入れる
        user = User()
        user.user_id = user_id
        user.username = username
        user.mail_address = mail_address
        user.password = UserDao.hash_password(password)
        user.save()

    @staticmethod
    def update_user(user_id:int, username:str, mail_address:str, password:str):
        """引数のユーザIDに紐づくユーザ情報を引数の値に更新する"""
        user = User.objects.get(user_id=user_id)
        if user:
            user.username = username
            user.mail_address = mail_address
            user.password = UserDao.hash_password(password)
            user.save()

    @staticmethod
    def update_user_without_password(user_id:int, username:str, mail_address:str):
        """引数のユーザIDに紐づくユーザ情報のうちパスワード以外を引数の値に更新する"""
        user = User.objects.get(user_id=user_id)
        if user:
            user.username = username
            user.mail_address = mail_address
            user.save()

    @staticmethod
    def delete_user_by_user_id(user_id: int):
        """ユーザIDに紐づくユーザを削除する"""
        User.objects.filter(user_id=user_id).delete()

    @staticmethod
    def test_session():
        return Session.objects.all()

    @staticmethod
    def update_user_password(user: User, password:str):
        user.password = UserDao.hash_password(password)
        user.save()

    @staticmethod
    def check_password_between_user_and_input(user: User, input_password: str):
        """引数で受け取ったパスワードとユーザ情報のパスワードが一致するか確認する"""
        return UserDao.check_password(user.password, input_password)

    @staticmethod
    def hash_password(password: str, rounds=12) -> str:
        """パスワードをハッシュ化して取得する"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def check_password(hash_password: str, input_password: str) -> str:
        """引数で受け取ったハッシュ化パスワードと文字列パスワードが一致するか確認する"""
        return bcrypt.checkpw(input_password.encode(), hash_password.encode())

class Lottery_pool(models.Model):
    """
    抽選申込情報を提供するDTOクラス
    """
    reservation_id =models.AutoField(_('予約ID'), primary_key=True)
    user_id = models.IntegerField(_('ユーザID'))
    username = models.CharField(_('ユーザ名'), max_length=40)
    check_in_date = models.DateField(_('チェックイン日'))
    check_out_date = models.DateField(_('チェックアウト日'))
    number_of_rooms = models.SmallIntegerField(_('部屋数'))
    number_of_guests = models.SmallIntegerField(_('宿泊人数'))
    priority = models.SmallIntegerField(_('希望') ,default=1)
    purpose = models.CharField(_('利用形態'), max_length=10, default=None)
    is_defeated = models.BooleanField(_('落選フラグ'), default=False)

class LotDao:
    """Lottery_poolオブジェクトを操作するクラス"""

    STATUS = 0

    @staticmethod
    def create_res_by_in_and_out(user_id: int, check_in_date: datetime.date, check_out_date: datetime.date, number_of_rooms: int, number_of_guests: int, purpose: str):
        """Lottery_poolオブジェクトを新規作成する"""
        if CalendarMaster.is_in_ngdate(check_in_date, check_out_date):
            return
        lot = Lottery_pool()
        lot.reservation_id = LodginDao.get_min_reservation_id()
        lot.user_id = user_id
        lot.username = UserDao.get_user(user_id).username
        lot.check_in_date = check_in_date
        lot.check_out_date = check_out_date
        lot.number_of_rooms = number_of_rooms
        lot.number_of_guests = number_of_guests
        lot.purpose = purpose
        lot.request_status = 1
        lot.expire_date = datetime.date.today() + datetime.timedelta(days=31)
        lot.is_defeated = False
        lot.save()

        # 滞在日数を導出
        visit_duration = (check_out_date - check_in_date).days

        # 宿泊データを作成
        LodginDao.create_lodging_data(lot.reservation_id, lot.user_id, check_in_date , visit_duration, lot.number_of_rooms)

    @staticmethod
    def get_res_list(user_id: int) -> list:
        """Lotteryオブジェクトを取得

        :param user_id ユーザID
        """
        return Lottery_pool.objects.filter(user_id=user_id)

    @staticmethod
    def get_res_by_reservation_id(reservation_id:int):
        """Lotteryオブジェクトを取得

        :param reservation_id 予約ID
        """
        return Lottery_pool.objects.get(reservation_id=reservation_id)

    @staticmethod
    def delete_by_reservation_id(reservation_id: int):
        """Lotteryオブジェクトを削除"""
        Lottery_pool.objects.filter(reservation_id=reservation_id).delete()

    @staticmethod
    def delete_by_user_id(user_id: int):
        """Lotteryオブジェクトを削除"""
        Lottery_pool.objects.filter(user_id=user_id).delete()

    @staticmethod
    def get_loginuserres_dto_by_user_id(user_id: str):
        """ログインユーザ情報に紐づくログインユーザDTOを取得"""
        lotterys = Lottery_pool.objects.filter(user_id=user_id)
        result = []
        if lotterys:
            for lot in lotterys:
                dto = LoginUserResInfo()
                dto.res_id = lot.reservation_id
                dto.app_status = 4 if lot.is_defeated else 0
                dto.check_in_date = lot.check_in_date
                dto.check_out_date = lot.check_out_date
                dto.number_of_rooms = lot.number_of_rooms
                dto.expire_date = ""
                dto.priority = lot.priority
                result.append(dto)
        return result


class Reservations(models.Model):
    """
    予約情報を提供するDTOクラス
    """
    reservation_id = models.IntegerField(_('予約ID'), primary_key=True)
    user_id = models.IntegerField(_('ユーザID'))
    username = models.CharField(_('ユーザ名'), max_length=40)
    check_in_date = models.DateField(_('チェックイン日'))
    check_out_date = models.DateField(_('チェックアウト日'))
    number_of_rooms = models.SmallIntegerField(_('部屋数'))
    number_of_guests = models.SmallIntegerField(_('宿泊人数'))
    purpose = models.CharField(_('利用形態'), max_length=10, default=None)
    lottery_flag = models.BooleanField(_('抽選フラグ'), default=True)
    request_status = models.SmallIntegerField(_('申込ステータス'))
    expire_date = models.DateField(_('有効期限'))

class ResDao:
    """Reservationsオブジェクトを操作するクラス"""

    @staticmethod
    def create_res_by_in_and_out(user_id: int, check_in_date: datetime.date, check_out_date: datetime.date, number_of_rooms: int, number_of_guests: int, purpose: str):
        """Reservationsオブジェクトを新規作成する"""
        if CalendarMaster.is_in_ngdate(check_in_date, check_out_date):
            return
        res = Reservations()
        res.reservation_id = LodginDao.get_min_reservation_id()
        res.user_id = user_id
        res.username = UserDao.get_user(user_id).username
        res.check_in_date = check_in_date
        res.check_out_date = check_out_date
        res.number_of_rooms = number_of_rooms
        res.number_of_guests = number_of_guests
        res.purpose = purpose
        res.request_status = 1
        res.expire_date = datetime.date.today() + datetime.timedelta(days=31)
        res.save()

        # 滞在日数を導出
        visit_duration = (check_out_date - check_in_date).days

        # 宿泊データを作成
        LodginDao.create_lodging_data(res.reservation_id, res.user_id, check_in_date , visit_duration, res.number_of_rooms)

    @staticmethod
    def create_res_by_lottery(reservation_id: int):
        """抽選情報から予約情報を作成する"""
        lot = LotDao.get_res_by_reservation_id(reservation_id)

        res = Reservations()
        res.reservation_id = lot.reservation_id
        res.user_id = lot.user_id
        res.username = UserDao.get_user(lot.user_id).username
        res.check_in_date = lot.check_in_date
        res.check_out_date = lot.check_out_date
        res.number_of_rooms = lot.number_of_rooms
        res.number_of_guests = lot.number_of_guests
        res.purpose = lot.purpose
        res.request_status = 1
        res.expire_date = datetime.date.today() + datetime.timedelta(days=31)
        res.save()

    @staticmethod
    def change_request_status_to_confirm(reservation_id: int):
        """予約情報の申込ステータスを確定させる"""
        res = ResDao.get_by_reservation_id(reservation_id)

        res.request_status = DETERMINED
        res.save()

    @staticmethod
    def change_request_status_to_cancel(reservation_id: int):
        """予約情報の申込ステータスを確定させる"""
        res = ResDao.get_by_reservation_id(reservation_id)

        res.request_status = CANCEL
        res.save()

    @staticmethod
    def check_overflowing_lodging_date(user_id: int, check_in_date: datetime.date, check_out_date: datetime.date) -> bool:
        """以下の2項目をチェック
        　・既に対象のユーザが予約してないか
        　・指定日の部屋数があふれていないか"""
        # 施設利用不可日かどうかを確認する
        if CalendarMaster.is_in_ngdate(check_in_date, check_out_date):
            return False

        rooms = {}

        stay_duration = (check_out_date - check_in_date).days

        # 宿泊日に部屋数が4部屋以上になってないかチェック
        for stay_number in range(stay_duration):
            lodging_date = check_in_date + datetime.timedelta(days=stay_number)
            rooms[lodging_date] = 0

            # 指定の日付に紐づく宿泊エンティティを取得
            lodgings = LodginDao.get_lodging_date_by_year_and_month_and_day(lodging_date.year, lodging_date.month, lodging_date.day)

            # 指定の日付の部屋数を全て合算した数値を取得
            rooms[lodging_date] = sum([lodging.number_of_rooms for lodging in lodgings])

            # ログインユーザが指定の日付で予約済の場合 False を返却
            if user_id in [ lod.user_id for lod in lodgings]:
                return False

            # 部屋数が5部屋以上となった場合 False を返却
            if rooms[lodging_date] > 3:
                return False

        # すべての宿泊日で部屋数が4部屋以内に収まれば True を返却
        return True

    @staticmethod
    def create_res_as_second_reservation(user_id: int, check_in_date: datetime.date, check_out_date: datetime.date, number_of_rooms: int, number_of_guests: int, purpose: str):
        """二次申込として予約を確定"""
        # 予約テーブルをロック
        with connection.cursor() as cursor:
            cursor.execute("LOCK TABLES accounts_reservations WRITE, accounts_lottery_pool WRITE, accounts_lodging WRITE, accounts_user READ, calendar_master READ")
            try:
                if ResDao.check_overflowing_lodging_date(user_id, check_in_date, check_out_date):
                    ResDao.create_res_by_in_and_out(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests, purpose)
                    return True
            finally:
                print("unlock is happned")
                cursor.execute("UNLOCK TABLES")

        return False

    @staticmethod
    def delete_by_reservation_id(reservation_id: int):
        """Lotteryオブジェクトを削除"""
        Reservations.objects.filter(reservation_id=reservation_id).delete()

    @staticmethod
    def delete_by_user_id(user_id: int):
        """Lotteryオブジェクトを削除"""
        Reservations.objects.filter(user_id=user_id).delete()

    @staticmethod
    def get_res_list(user_id: int) -> list:
        """ユーザIDに紐づくReservationオブジェクトを取得

        :param mail_address メールアドレス
        """
        return Reservations.objects.filter(user_id=user_id)

    @staticmethod
    def get_res_by_year_and_month(year:int, month:int):
        """引数の年月に紐づく予約情報を取得する"""
        return Reservations.objects.filter(check_in_date__year=year).filter(check_in_date__month=month).filter(request_status__lte=1)

    @staticmethod
    def get_res():
        """ユーザ情報でソートした予約情報を取得する"""
        return Reservations.objects.order_by('username')

    @staticmethod
    def get_res_by_month(month: int) -> Reservations:
        """
        引数の月度に該当する予約を取り出す
        :param month: 対象月度
        :return: 対象月度に該当するReservationsクラス
        """
        return Reservations.objects.filter(check_in_date__range=month)

    @staticmethod
    def get_by_reservation_id(reservation_id: int):
        """引数の予約IDに紐づく予約情報を取得する"""
        return Reservations.objects.get(reservation_id=reservation_id)

    @staticmethod
    def get_loginuserres_dto_by_user_id(user_id: str):
        """ログインユーザ情報に紐づくログインユーザDTOを取得"""
        reservations = Reservations.objects.filter(user_id=user_id)
        result = []
        if reservations:
            for res in reservations:
                dto = LoginUserResInfo()
                dto.res_id = res.reservation_id
                dto.app_status = (int)(res.request_status) + 1
                dto.check_in_date = res.check_in_date
                dto.check_out_date = res.check_out_date
                dto.number_of_rooms = res.number_of_rooms
                dto.expire_date = res.expire_date
                dto.priority = ""
                result.append(dto)
        return result


class Lodging(models.Model):
    """宿泊日数情報を提供するDTOクラス(予約クラスの子クラス)"""
    reservation_id = models.IntegerField(_('予約ID'))
    user_id = models.IntegerField(_("ユーザID"))
    lodging_date = models.DateField(_('宿泊日'))
    number_of_rooms = models.SmallIntegerField(_('部屋数'), default=1)


class LodginDao:

    @staticmethod
    def get_lodging_by_reservation_id(reservation_id:int):
        """予約IDに紐づく宿泊エンティティのQuerySetを返却"""
        return Lodging.objects.filter(reservation_id=reservation_id)

    @staticmethod
    def create_lodging_data(reservation_id: int, user_id: int, check_in_date: datetime.date , visit_duration: int, number_of_rooms: int):
        """予約エンティティと滞在日数を元に、宿泊エンティティを新規作成"""

        for vis_day in range(visit_duration):
            lodging = Lodging()
            lodging.user_id = user_id
            lodging.reservation_id = reservation_id
            lodging.lodging_date = check_in_date + datetime.timedelta(days=vis_day)
            lodging.number_of_rooms = number_of_rooms
            lodging.save()

    @staticmethod
    def get_lodging_date_by_year_and_month_and_day(year: int, month: int, day: int):
        """予約年月日をもとに、宿泊日エンティティを取得"""
        return Lodging.objects \
            .filter(lodging_date__year=year) \
            .filter(lodging_date__month=month) \
            .filter(lodging_date__day=day)

    @staticmethod
    def delete_by_reservation_id(reservation_id: int):
        """Lodgingオブジェクトを削除"""
        Lodging.objects.filter(reservation_id=reservation_id).delete()

    @staticmethod
    def delete_by_user_id(user_id: int):
        """Lotteryオブジェクトを削除"""
        Lodging.objects.filter(user_id=user_id).delete()

    @staticmethod
    def get_min_reservation_id():
        """最小の予約ID + 1を取得する """
        current = Lodging.objects.all().aggregate(Max('reservation_id'))['reservation_id__max']
        if current:
            return current + 1
        return 1

class Numbering(models.Model):
    """採番テーブル"""

    reservation_id = models.IntegerField(_("予約ID"))

class NumDao:

    @staticmethod
    @transaction.atomic
    def get_num():
        """採番地を更新(+1)して取得する"""
        num = Numbering.objects.select_for_update().first()
        num.reservation_id += 1
        num.save()
        return num.reservation_id

