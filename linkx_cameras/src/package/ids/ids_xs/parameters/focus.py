"""
IDSカメラパラメータのフォーカス用クラス．
IDSカメラパラメータ基本クラスを継承して作成し，パラメータ固有の処理のみ実装する．
基本的には抽象メソッドをオーバーライドした実装を行う．

"""
# IDSカメラライブラリ
from pyueye import ueye
# IDSカメラパラメータの基本クラス
from ...base_parameter_ids import BaseParameterIDS
# カメラパラメータ基本クラス用
from ....common import base_camera_tools as bct


class Focus(BaseParameterIDS):
    """
    IDSカメラパラメータのフォーカス用クラス．

    Methods
    ---------------------------------------
    __init__(camera: camra) -> None
        カメラオブジェクトを受け取り，フォーカスに関する値を取得できるように
        するためのメソッド．

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
        設定可能なフォーカスの最小値を返すメソッド．

    get_max_value() -> int
        抽象メソッドをオーバーライド．
        設定可能なフォーカスの最大値を返すメソッド．

    get_now_value() -> int
        抽象メソッドをオーバーライド．
        フォーカスの現在値を返すメソッド．

    get_now_status -> bool
        オートフォーカスがオンになっているかを返すメソッド．

    """
    def __init__(self, camera):
        """
        定義メソッド．
        インスタンス変数の宣言とオートフォーカスをオフにする．

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
        # オートフォーカスがオンになっているかを受け取る変数を宣言．
        self.__is_auto = ueye.c_uint()
        # オートフォーカスがオンになっている場合に表示するメッセージの
        # パラメータ固有部分を宣言
        self.__warning_name = "オートフォーカス"
        # パラメータ取得時のデータサイズを宣言．
        # uintは2bytesと4bytesがあるらしいが，ueyeでは4bytesのため4とする．
        self.data_size = 4

        # オートフォーカスをオフにする．
        nRet = ueye.is_Focus(
            self.__camera, ueye.FOC_CMD_SET_DISABLE_AUTOFOCUS, None, 0
        )
        return None

    @property
    def value(self):
        """"
        抽象メソッドをオーバーライド．
        カメラパラメータ基本クラスの定義により，
        camera.get_parameter実行時にはこのgetterが呼ばれる．

        get_min_value，get_now_value，get_max_value, get_now_statusメソッドを
        実行してフォーカスの最大値，最小値，現在値，オートフォーカスがオンに
        なっているかを取得する．

        Returns
        --------------------------------
        values: dict
            "max": フォーカスの最大値(int)
            "min": フォーカスの最小値(int)
            "now": フォーカスの現在値(int)
            "is_auto": オートフォーカスがオンになっているか(bool)

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
        camera.set_parameter(フォーカス変数名, value)実行時にはこのsetterが
        呼ばれる．

        set_parameterのvalueがデフォルトではbct.DummyValye()となっており，
        外部からset_parameter(フォーカス変数名)とset_parameter(
        フォーカス変数名, value: int)が実行された場合で異なる挙動をする．

        set_parameter(フォーカス変数名, value: int) -> None
            フォーカスをvalueに変更する．
            ただしオートフォーカスがオンの場合には標準出力に警告文を出力するのみ．

        set_parameter(フォーカス変数名) -> None
            オートフォーカスのオン，オフを切り替える．
            単に状態を反転させるため任意の状態に変更したい場合はget_parameterと
            組み合わせて条件分岐させる．

        Args
        ----------------------------
        value: int
            任意のフォーカス値．
            get_parameterメソッドでデフォルト値bct.DummyValue()が設定されている．

        """
        # オートフォーカス確認
        is_auto = self.get_now_status()
        # オートフォーカス-OFFの場合
        if is_auto is False:
            # フォーカス値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # ctypesで型変換
                new_value = ueye.c_int(int(value))
                # 値書き換え
                nRet = ueye.is_Focus(
                    self.__camera, ueye.FOC_CMD_SET_MANUAL_FOCUS,
                    new_value, self.data_size
                )
            # フォーカス値がない場合，オートフォーカス-ONへ切り替え
            else:
                nRet = ueye.is_Focus(
                    self.__camera, ueye.FOC_CMD_SET_ENABLE_AUTOFOCUS,
                    None, 0
                )
        # オートフォーカス-ONの場合
        else:
            # フォーカス値が与えられている場合
            if not isinstance(value, bct.DummyValue):
                # オートフォーカスのため切り替えられないことを出力
                self.msg_cannot_change_value(self.__warning_name)
            # フォーカス値がない場合，オートフォーカス-OFFへ切り替え
            else:
                nRet = ueye.is_Focus(
                    self.__camera, ueye.FOC_CMD_SET_DISABLE_AUTOFOCUS,
                    None, 0
                )
        return None

    def get_min_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なフォーカスの最小値を返すメソッド．

        Returns
        ---------------------
        self.__min_value.value: int
            self.__min_valueがctypes.uintのため.valueでint型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_Focus(
            self.__camera, ueye.FOC_CMD_GET_MANUAL_FOCUS_MIN,
            self.__min_value, self.data_size
        )
        return self.__min_value.value

    def get_max_value(self):
        """
        抽象メソッドをオーバーライド．
        設定可能なフォーカスの最大値を返すメソッド．

        Returns
        ---------------------
        self.__max_value.value: int
            self.__max_valueがctypes.uintのため.valueでint型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_Focus(
            self.__camera, ueye.FOC_CMD_GET_MANUAL_FOCUS_MAX,
            self.__max_value, self.data_size
        )
        return self.__max_value.value

    def get_now_value(self):
        """
        抽象メソッドをオーバーライド．
        フォーカスの現在値を返すメソッド．

        Returns
        ---------------------
        self.__now_value.value: int
            self.__now_valueがctypes.uintのため.valueでint型の値を取得して返す

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_Focus(
            self.__camera, ueye.FOC_CMD_GET_MANUAL_FOCUS,
            self.__now_value, self.data_size
        )
        return self.__now_value.value

    def get_now_status(self):
        """
        オートフォーカスがオンになっているかを返すメソッド．

        Returns
        ---------------------
        bool(self.__is_auto.value): bool
            self.__is_autoがctypes.uintであり，self._is_auto.valueが01の
            オートフォーカスがオンorオフで返ってくるためboolを用いて
            True，Falseに変換する．

        """
        # 本当はnRet != ueye.IS_SUCCESSでエラー処理
        nRet = ueye.is_Focus(
            self.__camera, ueye.FOC_CMD_GET_AUTOFOCUS_ENABLE,
            self.__is_auto, self.data_size
        )
        return bool(self.__is_auto.value)
