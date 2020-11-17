"""
ホワイトバランス(青)クラス．
IDSカメラパラメータ基本クラスを継承して作成し，パラメータ固有の処理のみ実装する．
基本的には抽象メソッドをオーバーライドした実装を行う．

"""
# IDSカメラライブラリ
from pyueye import ueye
# IDSカメラパラメータの基本クラス
from ...base_parameter_ids import BaseParameterIDS
# カメラパラメータ基本クラス用
from ....common import base_camera_tools as bct


class WhiteBalanceOffsetBlue(BaseParameterIDS):
    """
    ホワイトバランス(青)クラス．

    Methods
    ---------------------------------------
    __init__(camera: camra) -> None
        カメラオブジェクトを受け取り，ホワイトバランスに関する値を
        取得できるようにするためのメソッド．

    @property
    value() -> dict
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.get_parameter実行時にはこのgetterが呼ばれる．

    @value.setter
    value(value: int) -> None
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.set_parameter実行時にはこのsetterが呼ばれる．

    get_min_value() -> int
        抽象メソッドをオーバーライド．
        設定可能なホワイトバランス(青)の最小値を返すメソッド．

    get_max_value() -> int
        抽象メソッドをオーバーライド．
        設定可能なホワイトバランス(青)の最大値を返すメソッド．

    get_now_value() -> float
        抽象メソッドをオーバーライド．
        ホワイトバランス(青)の現在値を返すメソッド．

    get_now_status -> bool
        ホワイトバランス自動調整がオンになっているかを返すメソッド．

    """
    def __init__(self, camera):
        """
        定義メソッド．
        インスタンス変数の宣言とホワイトバランス自動調整をオフにする．

        Args
        -----------------------
        camera: camera
            カメラオブジェクト
            これでエラー処理を入れてもいいかも．

        """
        # カメラオブジェクトを保持
        self.__camera = camera
        # 最大値，最小値，現在値を受け取る変数を宣言．
        # またホワイトバランス(青)変更，取得時にホワイトバランス(青)も
        # 設定値，値格納用の変数が必要となるためそれようの値を定義
        # ctypes.double型で初期化する必要があるため，ueyeのメソッドを使用．
        self.__max_value = ueye.c_double()
        self.__min_value = ueye.c_double()
        self.__now_value = ueye.c_double()
        self.__sub_value = ueye.c_double()
        # ホワイトバランス自動調整がオンになっているかを受け取る変数を宣言．
        # doubleでないとエラーなことに注意．
        self.__is_auto = ueye.c_double()
        # パラメータ固有部分を宣言
        self.__warning_name = "ホワイトバランス自動調整"
        # 自動，手動の切り替えに使用するctypes.double型の変数を宣言．
        self.c_d_zero = ueye.c_double(0)
        self.enable = ueye.c_double(1)
        self.disable = ueye.c_double(0)
        # doubleが8bytesのため8
        self.data_size = 8

        # ホワイトバランス自動調整をオフにする．
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_WHITEBALANCE,
            self.disable, self.c_d_zero
        )
        return None

    @property
    def value(self):
        """"
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.get_parameter実行時にはこのgetterが呼ばれる．

        get_min_value，get_now_value，get_max_value, get_now_statusメソッドを
        実行してホワイトバランス(青)の最大値，最小値，現在値，
        ホワイトバランス自動調整がオンになっているかを取得する．

        Returns
        --------------------------------
        values: dict
            "max": ホワイトバランス(青)の最大値(float)
            "min": ホワイトバランス(青)の最小値(float)
            "now": ホワイトバランス(青)の現在値(float)
            "is_auto": ホワイトバランス自動調整がオンになっているか(bool)

        """
        values = {
            "min": self.get_min_value(),
            "now": self.get_now_value(),
            "max": self.get_max_value(),
            "is_auto": self.get_now_status(),
        }
        return values

    @value.setter
    def value(self, value=None):
        """
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.set_parameter実行時にはこのsetterが呼ばれる．

        set_parameterのvalueがデフォルトではbct.DummyValye()となっており，
        外部からset_parameter(ホワイトバランス(青)変数名)とset_parameter(
        ホワイトバランス(青)変数名, value: float)が実行された場合で異なる挙動をする．

        set_parameter(ホワイトバランス(青)変数名, value: float) -> None
            ホワイトバランス(青)をvalueに変更する．
            ただしホワイトバランス自動調整がオンの場合には標準出力に警告文を
            出力するのみ．

        set_parameter(ホワイトバランス(青)変数名) -> None
            ホワイトバランス自動調整のオン，オフを切り替える．
            単に状態を反転させるため任意の状態に変更したい場合はget_parameterと
            組み合わせて条件分岐させる．

        Args
        ----------------------------
        value: float
            任意のホワイトバランス(青)値．
            get_parameterメソッドでデフォルト値bct.DummyValue()が設定されている．

        """
        # ホワイトバランス自動調整確認
        auto_gain = self.get_now_status()
        # ホワイトバランス自動調整-OFFの場合
        if auto_gain is False:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # ctypesで型変換
                new_value = ueye.c_double(float(value))
                # 現在のゲイン(青)を取得するためにget_now_value実行．
                _ = self.get_now_value()
                # 値書き換え
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_AUTO_WB_OFFSET,
                    self.__sub_value, new_value
                )
            # 値が与えられていない場合，ホワイトバランス自動調整-ONへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_WHITEBALANCE,
                    self.enable, self.c_d_zero
                )
        # ホワイトバランス自動調整-ONの場合
        else:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # ホワイトバランス自動調整のため切り替えられないことを出力
                self.msg_cannot_change_value(self.__warning_name)
            # 値が与えられていない場合，ホワイトバランス自動調整-OFFへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_WHITEBALANCE,
                    self.disable, self.c_d_zero
                )
        return None

    def get_min_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なホワイトバランス(青)の最小値を返すメソッド．

        Returns
        --------------------
        self.__min_value.value: float
            設定可能なホワイトバランス(青)の最小値
            self.__min_valueがctypes.doubleのため.valueでfloat型の値を取得して返す

        """
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_GET_AUTO_WB_OFFSET_MIN,
            self.__sub_value, self.__min_value
        )
        return self.__min_value.value

    def get_max_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なホワイトバランス(青)の最小値を返すメソッド．

        Returns
        --------------------
        self.__max_value.value: float
            設定可能なホワイトバランス(青)の最大値
            self.__max_valueがctypes.doubleのため.valueでfloat型の値を取得して返す

        """
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_GET_AUTO_WB_OFFSET_MAX,
            self.__sub_value, self.__max_value
        )
        return self.__max_value.value

    def get_now_value(self):
        """
        抽象メソッドをオーバーライド．
        ホワイトバランス(青)の現在値を返すメソッド．

        Returns
        ---------------------
        self.__now_value.value: float
            ホワイトバランス(青)の現在値
            self.__now_valueがctypes.doubleのため.valueでfloat型の値を取得して返す

        """
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_GET_AUTO_WB_OFFSET,
            self.__sub_value, self.__now_value
        )
        return self.__now_value.value

    def get_now_status(self):
        """
        ホワイトバランス自動調整がオンになっているかを返すメソッド．

        Returns
        ---------------------
        bool(self.__is_auto.value): bool
            self.__is_autoがctypes.doubleであり，self._is_auto.valueが01の
            ホワイトバランス自動調整がオンorオフで返ってくるためboolを
            用いてTrue，Falseに変換する．

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_WHITEBALANCE,
            self.__is_auto, self.c_d_zero
        )
        return bool(self.__is_auto.value)
