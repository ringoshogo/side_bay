
class LoginUserResInfo:
    """ログインの抽選／予約情報を保持"""

    def __init__(self):
        self.res_id = None
        self.app_status = None
        self.check_in_date  = None
        self.check_out_date = None
        self.number_of_rooms  = None
        self.expire_date = None
        self.priority  = None
