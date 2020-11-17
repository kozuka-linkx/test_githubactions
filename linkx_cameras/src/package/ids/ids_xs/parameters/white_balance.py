"""
IDSカメラパラメータのホワイトバランス用クラス．
IDSカメラパラメータ基本クラスを継承して作成し，パラメータ固有の処理のみ実装する．
基本的には抽象メソッドをオーバーライドした実装を行う．

またこのクラスを使用するカメラではホワイトバランスの設定として色温度(K)の設定を
行うことに注意する．

"""
# IDSカメラライブラリ
from pyueye import ueye
# IDSカメラパラメータの基本クラス
from ...base_parameter_ids import BaseParameterIDS
# カメラパラメータ基本クラス用
from ....common import base_camera_tools as bct


class WhiteBalance(BaseParameterIDS):
    """
    IDSカメラパラメータのホワイトバランス用クラス．

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
        設定可能なホワイトバランスの最小値を返すメソッド．

    get_max_value() -> int
        抽象メソッドをオーバーライド．
        設定可能なホワイトバランスの最大値を返すメソッド．

    get_now_value() -> int
        抽象メソッドをオーバーライド．
        ホワイトバランスの現在値を返すメソッド．

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
        # ctypes.uint型で初期化する必要があるため，ueyeのメソッドを使用．
        self.__min_value = ueye.c_uint()
        self.__max_value = ueye.c_uint()
        self.__now_value = ueye.c_uint()
        # ホワイトバランス自動調整がオンになっているかを受け取る変数を宣言．
        # doubleでないとエラーなことに注意．
        self.__is_auto = ueye.c_double()
        # パラメータ固有部分を宣言
        self.__warning_name = "ホワイトバランス自動調整"
        # 自動，手動の切り替えに使用するctypes.double型の変数を宣言．
        self.c_d_zero = ueye.c_double(0)
        self.enable = ueye.c_double(1)
        self.disable = ueye.c_double(0)
        # パラメータ取得時のデータサイズを宣言．
        # uintは2bytesと4bytesがあるらしいが，ueyeでは4bytesのため4とする．
        self.data_size = 4

        # ホワイトバランス自動調整をオフにする．
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_SET_ENABLE_AUTO_WHITEBALANCE,
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
        実行してホワイトバランスの最大値，最小値，現在値，
        ホワイトバランス自動調整がオンになっているかを取得する．

        Returns
        --------------------------------
        values: dict
            "max": ホワイトバランスの最大値(int)
            "min": ホワイトバランスの最小値(int)
            "now": ホワイトバランスの現在値(int)
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
    def value(self, value):
        """
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.set_parameter(ホワイトバランス変数名, value)実行時にはこのsetterが
        呼ばれる．

        set_parameterのvalueがデフォルトではbct.DummyValye()となっており，
        外部からset_parameter(ホワイトバランス変数名)とset_parameter(
        ホワイトバランス変数名, value: int)が実行された場合で異なる挙動をする．

        set_parameter(ホワイトバランス変数名, value: int) -> None
            ホワイトバランスをvalueに変更する．
            ただしホワイトバランス自動調整がオンの場合には標準出力に警告文を
            出力するのみ．

        set_parameter(ホワイトバランス変数名) -> None
            ホワイトバランス自動調整のオン，オフを切り替える．
            単に状態を反転させるため任意の状態に変更したい場合はget_parameterと
            組み合わせて条件分岐させる．

        Args
        ----------------------------
        value: int
            任意のホワイトバランス値．
            get_parameterメソッドでデフォルト値bct.DummyValue()が設定されている．

        """
        # ホワイトバランス自動調整確認
        is_auto = self.get_now_status()
        # ホワイトバランス自動調整-OFFの場合
        if is_auto is False:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # ctypesで型変換
                new_value = ueye.c_uint(int(value))
                # 値書き換え
                nRet = ueye.is_ColorTemperature(
                    self.__camera, ueye.COLOR_TEMPERATURE_CMD_SET_TEMPERATURE,
                    new_value, self.data_size
                )
            # 値が与えられていない場合，ホワイトバランス自動調整-ONへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_WHITEBALANCE,
                    self.enable, self.c_d_zero
                )
        # ホワイトバランス自動調整-ONの場合
        else:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                self.msg_cannot_change_value(self.__warning_name)
            # 時間が与えられていない場合，ホワイトバランス自動調整-OFFへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_WHITEBALANCE,
                    self.disable, self.c_d_zero
                )
        return None

    def get_min_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なホワイトバランスの最小値を返すメソッド．

        Returns
        ---------------------
        self.__min_value.value: int
            self.__min_valueがctypes.uintのため.valueでint型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_ColorTemperature(
            self.__camera, ueye.COLOR_TEMPERATURE_CMD_GET_TEMPERATURE_MIN,
            self.__min_value, self.data_size
        )
        return self.__min_value.value

    def get_max_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なホワイトバランスの最大値を返すメソッド．

        Returns
        ---------------------
        self.__max_value.value: int
            self.__max_valueがctypes.uintのため.valueでint型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_ColorTemperature(
            self.__camera, ueye.COLOR_TEMPERATURE_CMD_GET_TEMPERATURE_MAX,
            self.__max_value, self.data_size
        )
        return self.__max_value.value

    def get_now_value(self):
        """
        抽象メソッドをオーバーライド．
        ホワイトバランスの現在値を返すメソッド．

        Returns
        ---------------------
        self.__now_value.value: int
            self.__now_valueがctypes.uintのため.valueでint型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_ColorTemperature(
            self.__camera, ueye.COLOR_TEMPERATURE_CMD_GET_TEMPERATURE,
            self.__now_value, self.data_size
        )
        return self.__now_value.value

    def get_now_status(self):
        """
        ホワイトバランス自動調整がオンになっているかを返すメソッド．

        Returns
        ---------------------
        bool(self.__is_auto.value): bool
            self.__is_autoがctypes.doubleであり，self._is_auto.valueが01の
            ホワイトバランス自動調整がオンorオフで返ってくるためboolを用いて
            True，Falseに変換する．

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_GET_ENABLE_AUTO_WHITEBALANCE,
            self.__is_auto, self.c_d_zero
        )
        return bool(self.__is_auto.value)
