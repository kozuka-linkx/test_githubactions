"""
IDSカメラパラメータのシャッタースピード用クラス．
IDSカメラパラメータ基本クラスを継承して作成し，パラメータ固有の処理のみ実装する．
基本的には抽象メソッドをオーバーライドした実装を行う．

またこのクラスを使用するカメラではシャッタースピードをミリ秒で設定することに
注意する．

"""
# IDSカメラライブラリ
from pyueye import ueye
# IDSカメラパラメータの基本クラス
from ...base_parameter_ids import BaseParameterIDS
# カメラパラメータ基本クラス用
from ....common import base_camera_tools as bct


class Shutter(BaseParameterIDS):
    """
    IDSカメラパラメータのシャッタースピード用クラス．

    Methods
    ---------------------------------------
    __init__(camera: camra) -> None
        カメラオブジェクトを受け取り，シャッタースピードに関する値を
        取得できるようにするためのメソッド．

    @property
    value() -> dict
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.get_parameter実行時にはこのgetterが呼ばれる．

    @value.setter
    value(value: float) -> None
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.set_parameter実行時にはこのsetterが呼ばれる．

    get_min_value() -> float
        抽象メソッドをオーバーライド．
        設定可能なシャッタースピードの最小値を返すメソッド．

    get_max_value() -> float
        抽象メソッドをオーバーライド．
        設定可能なシャッタースピードの最大値を返すメソッド．

    get_now_value() -> float
        抽象メソッドをオーバーライド．
        シャッタースピードの現在値を返すメソッド．

    get_now_status -> bool
        シャッタースピード自動調整がオンになっているかを返すメソッド．

    """
    def __init__(self, camera):
        """
        定義メソッド．
        インスタンス変数の宣言とシャッタースピード自動調整をオフにする．

        Args
        -----------------------
        camera: camera
            カメラオブジェクト
            これでエラー処理を入れてもいいかも．

        """
        # カメラオブジェクトを保持
        self.__camera = camera
        # 最小値，最大値，現在値を受け取る変数を宣言．
        # ctypes.double型で初期化する必要があるため，ueyeのメソッドを使用．
        self.__min_value = ueye.c_double()
        self.__max_value = ueye.c_double()
        self.__now_value = ueye.c_double()
        # シャッタースピード自動調整がオンになっているかを受け取る変数を宣言．
        # doubleでないとエラーなことに注意．
        self.__is_auto = ueye.c_double()
        # パラメータ固有部分を宣言
        self.__warning_name = "シャッタースピード自動調整"

        # 自動，手動の切り替えに使用するctypes.double型の変数を宣言．
        self.c_d_zero = ueye.c_double(0)
        self.enable = ueye.c_double(1)
        self.disable = ueye.c_double(0)
        # doubleが8bytesのため8
        self.data_size = 8

        # シャッタースピード自動調整をオフにする．
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_SET_ENABLE_AUTO_SHUTTER,
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
        実行してシャッタースピードの最大値，最小値，現在値，
        シャッタースピード自動調整がオンになっているかを取得する．

        Returns
        --------------------------------
        values: dict
            "max": シャッタースピードの最大値(float)
            "min": シャッタースピードの最小値(float)
            "now": シャッタースピードの現在値(float)
            "is_auto": シャッタースピード自動調整がオンになっているか(bool)

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
        camera.set_parameter実行時にはこのsetterが呼ばれる．

        set_parameterのvalueがデフォルトではbct.DummyValye()となっており，
        外部からset_parameter(シャッタースピード変数名)とset_parameter(
        シャッタースピード変数名, value: float)が実行された場合で異なる挙動をする．

        set_parameter(シャッタースピード変数名, value: float) -> None
            シャッタースピードをvalueに変更する．
            ただしシャッタースピード自動調整がオンの場合には標準出力に警告文を
            出力するのみ．

        set_parameter(シャッタースピード変数名) -> None
            シャッタースピード自動調整のオン，オフを切り替える．
            単に状態を反転させるため任意の状態に変更したい場合はget_parameterと
            組み合わせて条件分岐させる．

        Args
        ----------------------------
        value: float
            任意のシャッタースピード値．
            get_parameterメソッドでデフォルト値bct.DummyValue()が設定されている．

        """
        # シャッタースピード自動調整確認
        is_auto = self.get_now_status()
        # シャッタースピード自動調整-OFFの場合
        if is_auto is False:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # ctypesで型変換
                new_value = ueye.c_double(value)
                # 値書き換え
                nRet = ueye.is_Exposure(
                    self.__camera, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,
                    new_value, self.data_size
                )
            # 値が与えられていない場合，シャッタースピード自動調整-ONへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_SHUTTER,
                    self.enable, self.c_d_zero
                )
        # シャッタースピード自動調整-ONの場合
        else:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # シャッタースピード自動調整のため切り替えられないことを出力
                self.msg_cannot_change_value(self.__warning_name)
            # 値が与えられていない場合，シャッタースピード自動調整-OFFへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_SHUTTER,
                    self.disable, self.c_d_zero
                )
        return None

    def get_min_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なシャッタースピードの最小値を返すメソッド．

        Returns
        ---------------------
        self.__min_value.value: float
            self.__min_valueがctypes.doubleのため.valueでfloat型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_Exposure(
            self.__camera, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MIN,
            self.__min_value, self.data_size
        )
        return self.__min_value.value

    def get_max_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なシャッタースピードの最大値を返すメソッド．

        Returns
        ---------------------
        self.__max_value.value: float
            self.__max_valueがctypes.doubleのため.valueでfloat型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_Exposure(
            self.__camera, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MAX,
            self.__max_value, self.data_size
        )
        return self.__max_value.value

    def get_now_value(self):
        """
        抽象メソッドをオーバーライド．
        シャッタースピードの現在値を返すメソッド．

        Returns
        ---------------------
        self.__now_value.value: float
            self.__now_valueがctypes.doubleのため.valueでfloat型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_Exposure(
            self.__camera, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE,
            self.__now_value, self.data_size
        )
        return self.__now_value.value

    def get_now_status(self):
        """
        シャッタースピード自動調整がオンになっているかを返すメソッド．

        Returns
        ---------------------
        bool(self.__is_auto.value): bool
            self.__is_autoがctypes.doubleであり，self._is_auto.valueが01の
            シャッタースピード自動調整がオンorオフで返ってくるためboolを用いて
            True，Falseに変換する．

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_GET_ENABLE_AUTO_SHUTTER,
            self.__is_auto, self.c_d_zero
        )
        return bool(self.__is_auto.value)
