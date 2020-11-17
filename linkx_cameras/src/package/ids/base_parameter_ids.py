"""
IDSカメラパラメータ基本クラスBaseParameterIDSの定義．
カメラパラメータ基本クラスBaseParameterを継承している．
このクラス自体はIDSカメラ基本クラスなため，運用上はカメラ固有クラスの
CameraIDS_BoardやCameraIDS_XSを使用する．


==============================================================================
現時点で実装済みのパラメータクラス
==============================================================================
GainShutter_Gain:
    ゲインとシャッタースピードを独立して
    自動，手動切り替えられないカメラのゲインクラス
GainShutter_Shutter
    ゲインとシャッタースピードを独立して
    自動，手動切り替えられないカメラのシャッタースピードクラス
Gain
    ゲインを独立して自動，手動切り替えられるカメラのゲインクラス
Shutter
    シャッタースピードを独立して自動，手動切り替えられるカメラの
    シャッタースピードクラス
WhiteBalance
    ホワイトバランスクラス
    RGBのホワイトバランスを変更するのではなく，色温度で調整を行うことに注意．
Focus
    フォーカスクラス

"""
from abc import ABCMeta
# カメラパラメータ基本クラス用
from ..common import base_camera_tools as bct

__author__ = "LiNKX"
__copyright__ = "Copyright 2020, LiNKX Inc,"
__credits__ = ["Toshiki Kozuka"]
__license__ = "*********UNDEFINED**********"
__version__ = "0.1.0"
__maintainer__ = "Toshiki Kozuka"
__email__ = "kozuka@linkx.dev"
__status__ = "Dev"
__data__ = "2020/10/23"


class BaseParameterIDS(bct.BaseParameter, metaclass=ABCMeta):
    """
    BaseParameterで実装済みのメソッド以外にIDSカメラパラメータで
    共通するメソッドを定義する．

    Methods
    ----------------------------
    msg_cannot_change_value(target: str) -> None
        自動調整がオンになっており，パラメータの手動変更が不可であることを
        標準出力に出力するためのメソッド．

    """
    def msg_cannot_change_value(self, target):
        """
        自動調整がオンになっており，パラメータの手動変更が不可であることを
        標準出力に出力するためのメソッド．
        外部から直接呼ばず，パラメータの値を変更するメソッド中で呼ぶ．

        (targetが"オートフォーカス"の場合の標準出力例)
            WARNING: オートフォーカスが有効のため値を変更できません

        Args
        ------------------------------------
        target: str
            何のパラメータが自動調整になっているかを示す文字列．

        """
        bct.PrintMessage.cannot_change_value(target)
        return None
