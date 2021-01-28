"""
IDSカメラパラメータのゲインとシャッタースピードを独立して自動，手動を
切り替えられない場合のゲイン用クラス．
IDSカメラパラメータ基本クラスを継承して作成し，パラメータ固有の処理のみ実装する．
基本的には抽象メソッドをオーバーライドした実装を行う．

またこのクラスを使用するカメラではゲインの設定として色温度(K)の設定を
行うことに注意する．

"""
# IDSカメラライブラリ
from pyueye import ueye
# IDSカメラパラメータの基本クラス
from ...base_parameter_ids import BaseParameterIDS
# カメラパラメータ基本クラス用
from ....common import base_camera_tools as bct


class GainShutter_Gain(BaseParameterIDS):
    """
    IDSカメラパラメータのゲインとシャッタースピードを独立して自動，手動を
    切り替えられない場合のゲイン用クラス．

    Methods
    ---------------------------------------
    __init__(camera: camra) -> None
        カメラオブジェクトを受け取り，ゲインに関する値を
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
        設定可能なゲインの最小値を返すメソッド．

    get_max_value() -> int
        抽象メソッドをオーバーライド．
        設定可能なゲインの最大値を返すメソッド．

    get_now_value() -> float
        抽象メソッドをオーバーライド．
        ゲインの現在値を返すメソッド．

    get_now_status -> bool
        ゲイン自動調整がオンになっているかを返すメソッド．

    """
    def __init__(self, camera):
        """
        定義メソッド．
        インスタンス変数の宣言とゲイン・シャッタースピード自動調整をオフにする．

        Args
        -----------------------
        camera: camera
            カメラオブジェクト
            これでエラー処理を入れてもいいかも．

        """
        # カメラオブジェクトを保持
        self.__camera = camera
        # 現在値を受け取る変数を宣言．
        # 内部で0-100に正規化されているため最大値は100，最小値は0で固定
        # ctypes.double型で初期化する必要があるため，ueyeのメソッドを使用．
        self.__now_value = ueye.c_double()
        # ゲイン自動調整がオンになっているかを受け取る変数を宣言．
        # doubleでないとエラーなことに注意．
        self.__is_auto = ueye.c_double()
        # パラメータ固有部分を宣言
        self.__warning_name = "ゲイン及びシャッタースピード自動調整"
        # 自動，手動の切り替えに使用するctypes.double型の変数を宣言．
        self.c_d_zero = ueye.c_double(0)
        self.enable = ueye.c_double(1)
        self.disable = ueye.c_double(0)
        # doubleが8bytesのため8
        self.data_size = 8

        # ゲイン・シャッタースピード自動調整をオフにする．
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_GAIN_SHUTTER,
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
        実行してゲインの最大値，最小値，現在値，
        ゲイン自動調整がオンになっているかを取得する．

        Returns
        --------------------------------
        values: dict
            "max": ゲインの最大値(int)
            "min": ゲインの最小値(int)
            "now": ゲインの現在値(float)
            "is_auto": ゲイン自動調整がオンになっているか(bool)

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
        外部からset_parameter(ゲイン変数名)とset_parameter(ゲイン変数名,
        value: int)が実行された場合で異なる挙動をする．

        set_parameter(ゲイン変数名, value: int) -> None
            ゲインをvalueに変更する．
            ただしゲイン自動調整がオンの場合には標準出力に警告文を
            出力するのみ．

        set_parameter(ゲイン変数名) -> None
            ゲイン自動調整のオン，オフを切り替える．
            単に状態を反転させるため任意の状態に変更したい場合はget_parameterと
            組み合わせて条件分岐させる．

        Args
        ----------------------------
        value: int
            任意のゲイン値．
            get_parameterメソッドでデフォルト値bct.DummyValue()が設定されている．

        """
        # ゲイン自動調整確認
        auto_gain = self.get_now_status()
        # ゲイン自動調整-OFFの場合
        if auto_gain is False:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # ctypesで型変換
                # 値取得時にはdoubleだが，値設定時にdoubleを与えるとエラーが
                # 発生するためintで渡す．
                new_value = ueye.c_int(int(value))
                # 値書き換え
                nRet = ueye.is_SetHardwareGain(
                    self.__camera, new_value, ueye.IS_IGNORE_PARAMETER,
                    ueye.IS_IGNORE_PARAMETER, ueye.IS_IGNORE_PARAMETER
                )
            # 値が与えられていない場合，ゲイン自動調整-ONへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_GAIN_SHUTTER,
                    self.enable, self.c_d_zero
                )
        # ゲイン自動調整-ONの場合
        else:
            # 値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # ゲイン自動調整のため切り替えられないことを出力
                self.msg_cannot_change_value(self.__warning_name)
            # 値が与えられていない場合，ゲイン自動調整-OFFへ切り替え
            else:
                nRet = ueye.is_SetAutoParameter(
                    self.__camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_GAIN_SHUTTER,
                    self.disable, self.c_d_zero
                )
        return None

    def get_min_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なゲインの最小値を返すメソッド．
        内部で0-100に正規化されているため最小値は固定値．

        Returns
        --------------------
        0: int
            数値

        """
        return 0

    def get_max_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なゲインの最小値を返すメソッド．
        内部で0-100に正規化されているため最大値は固定値．

        Returns
        --------------------
        100: int
            数値

        """
        return 100

    def get_now_value(self):
        """
        抽象メソッドをオーバーライド．
        ゲインの現在値を返すメソッド．

        Returns
        ---------------------
        self.__now_value.value: float
            self.__now_valueがctypes.doubleのため.valueでfloat型の値を取得して返す

        """
        # 返り値が値そのもの(float)
        self.__now_value.value = ueye.is_SetHardwareGain(
            self.__camera, ueye.IS_GET_MASTER_GAIN, ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER, ueye.IS_IGNORE_PARAMETER
        )
        return self.__now_value.value

    def get_now_status(self):
        """
        ゲイン・シャッタースピード自動調整がオンになっているかを返すメソッド．

        Returns
        ---------------------
        bool(self.__is_auto.value): bool
            self.__is_autoがctypes.doubleであり，self._is_auto.valueが01の
            ゲイン・シャッタースピード自動調整がオンorオフで返ってくるためboolを
            用いてTrue，Falseに変換する．

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_SetAutoParameter(
            self.__camera, ueye.IS_GET_ENABLE_AUTO_SENSOR_GAIN_SHUTTER,
            self.__is_auto, self.c_d_zero
        )
        return bool(self.__is_auto.value)
